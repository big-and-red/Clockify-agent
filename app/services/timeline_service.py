from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import asyncio
import structlog

from app.services.clockify_client import ClockifyClient
from app.schemas.response import (
    DailyTimelineResponse, ProjectTimelineResponse, 
    DayData, ProjectData, ProjectDayData, TimeBlock,
    DailySummary, ProjectTimelineSummary, ProjectSummary
)
from app.schemas.clockify import ClockifyTimeEntry
from app.utils.time_formatter import (
    parse_clockify_time, calculate_duration, calculate_hours,
    format_time_only, merge_adjacent_blocks, format_duration,
    format_session_duration
)

logger = structlog.get_logger()

class TimelineService:
    def __init__(self):
        self.clockify_client = ClockifyClient()
    
    async def get_daily_timeline(self, start_date: date, end_date: date) -> DailyTimelineResponse:
        """Получает ежедневную временную шкалу за указанный период"""
        logger.info("Processing daily timeline request", start_date=start_date, end_date=end_date)
        
        # Получаем временные записи
        entries = await self.clockify_client.get_time_entries(start_date, end_date)
        
        # Группируем по дням
        days_data = await self._group_by_days(entries)
        
        # Рассчитываем статистику
        summary = self._calculate_daily_summary(days_data, start_date, end_date)
        
        logger.info("Daily timeline processed successfully", 
                   active_days=summary.active_days, 
                   total_time=summary.total_time)
        
        return DailyTimelineResponse(days=days_data, summary=summary)
    
    async def get_project_timeline(self, start_date: date, end_date: date, project_name: str) -> ProjectTimelineResponse:
        """Получает временную шкалу для конкретного проекта"""
        logger.info("Processing project timeline request", 
                   start_date=start_date, end_date=end_date, project=project_name)
        
        # Проверяем существование проекта
        project = await self.clockify_client.get_project_by_name(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        
        # Получаем временные записи
        entries = await self.clockify_client.get_time_entries(start_date, end_date)
        
        # Группируем по дням
        days_data = await self._group_project_by_days(entries, project_name)
        
        # Рассчитываем статистику
        summary = self._calculate_project_summary(days_data, start_date, end_date)
        
        logger.info("Project timeline processed successfully", 
                   project=project_name,
                   active_days=summary.active_days, 
                   total_time=summary.total_time)
        
        return ProjectTimelineResponse(
            project_name=project_name,
            days=days_data,
            summary=summary
        )
    
    async def _group_by_days(self, entries: List[ClockifyTimeEntry]) -> Dict[str, DayData]:
        """Группирует записи по дням и проектам"""
        days_data = defaultdict(lambda: defaultdict(list))
        
        # Получаем все проекты для маппинга ID -> название
        projects = await self.clockify_client.get_projects()
        project_map = {project.id: project.name for project in projects}
        
        for entry in entries:
            if not entry.timeInterval.get("end"):  # Пропускаем активные записи
                continue
            
            start_time = parse_clockify_time(entry.timeInterval["start"])
            end_time = parse_clockify_time(entry.timeInterval["end"])
            
            day_key = start_time.date().isoformat()
            
            # Получаем название проекта
            project_name = "Unnamed"
            if entry.projectId and entry.projectId in project_map:
                project_name = project_map[entry.projectId]
            
            # Сохраняем описание временной записи
            description = entry.description if entry.description else None
            
            days_data[day_key][project_name].append((start_time, end_time, description))
        
        # Обрабатываем каждый день
        result = {}
        for day_key, projects in days_data.items():
            day_projects = {}
            day_total = 0.0
            
            for project_name, time_blocks in projects.items():
                # Объединяем соседние блоки (но сохраняем описания)
                merged_blocks = self._merge_adjacent_blocks_with_descriptions(time_blocks)
                
                # Создаем TimeBlock объекты
                formatted_blocks = []
                project_total = 0.0
                
                for start, end, description in merged_blocks:
                    duration_str = calculate_duration(start, end)
                    hours = calculate_hours(start, end)
                    project_total += hours
                    
                    formatted_blocks.append(TimeBlock(
                        start_time=format_time_only(start),
                        end_time=format_time_only(end),
                        duration=duration_str,
                        description=description
                    ))
                
                day_projects[project_name] = ProjectData(
                    total_hours=round(project_total, 1),
                    time_blocks=formatted_blocks,
                    description=None  # Убираем описание проекта, оставляем только описание временных блоков
                )
                day_total += project_total
            
            result[day_key] = DayData(
                projects=day_projects,
                day_total=round(day_total, 1)
            )
        
        return result
    
    def _merge_adjacent_blocks_with_descriptions(self, blocks: List[Tuple[datetime, datetime, Optional[str]]]) -> List[Tuple[datetime, datetime, Optional[str]]]:
        """Объединяет соседние временные блоки с сохранением описаний"""
        if not blocks:
            return []
        
        # Sort by start time
        sorted_blocks = sorted(blocks, key=lambda x: x[0])
        merged = [sorted_blocks[0]]
        
        for current_start, current_end, current_desc in sorted_blocks[1:]:
            last_start, last_end, last_desc = merged[-1]
            
            # Check if gap is less than 5 minutes
            gap = (current_start - last_end).total_seconds() / 60
            if gap <= 5:
                # Merge blocks - объединяем описания если они есть
                merged_description = None
                if last_desc and current_desc:
                    merged_description = f"{last_desc}, {current_desc}"
                elif last_desc:
                    merged_description = last_desc
                elif current_desc:
                    merged_description = current_desc
                
                merged[-1] = (last_start, max(last_end, current_end), merged_description)
            else:
                merged.append((current_start, current_end, current_desc))
        
        return merged
    
    async def _group_project_by_days(self, entries: List[ClockifyTimeEntry], project_name: str) -> Dict[str, ProjectDayData]:
        """Группирует записи проекта по дням"""
        days_data = defaultdict(list)
        
        # Получаем все проекты для маппинга ID -> название
        projects = await self.clockify_client.get_projects()
        project_map = {project.id: project.name for project in projects}
        
        # Находим ID проекта по названию
        project_id = None
        for pid, pname in project_map.items():
            if pname == project_name:
                project_id = pid
                break
        
        if not project_id:
            return {}
        
        for entry in entries:
            if not entry.timeInterval.get("end"):  # Пропускаем активные записи
                continue
            
            if entry.projectId != project_id:  # Фильтруем только нужный проект
                continue
            
            start_time = parse_clockify_time(entry.timeInterval["start"])
            end_time = parse_clockify_time(entry.timeInterval["end"])
            
            day_key = start_time.date().isoformat()
            description = entry.description if entry.description else None
            days_data[day_key].append((start_time, end_time, description))
        
        # Обрабатываем каждый день
        result = {}
        for day_key, time_blocks in days_data.items():
            # Объединяем соседние блоки с сохранением описаний
            merged_blocks = self._merge_adjacent_blocks_with_descriptions(time_blocks)
            
            # Создаем TimeBlock объекты
            formatted_blocks = []
            day_total = 0.0
            
            for start, end, description in merged_blocks:
                duration_str = calculate_duration(start, end)
                hours = calculate_hours(start, end)
                day_total += hours
                
                formatted_blocks.append(TimeBlock(
                    start_time=format_time_only(start),
                    end_time=format_time_only(end),
                    duration=duration_str,
                    description=description
                ))
            
            result[day_key] = ProjectDayData(
                total_hours=round(day_total, 1),
                time_blocks=formatted_blocks
            )
        
        return result
    
    def _calculate_daily_summary(self, days_data: Dict[str, DayData], start_date: date, end_date: date) -> DailySummary:
        """Рассчитывает сводку для ежедневной временной шкалы"""
        active_days = len(days_data)
        period_str = f"{start_date.isoformat()} to {end_date.isoformat()}"
        
        # Собираем статистику по проектам
        project_totals = defaultdict(float)
        total_hours = 0.0
        
        for day_data in days_data.values():
            total_hours += day_data.day_total
            for project_name, project_data in day_data.projects.items():
                project_totals[project_name] += project_data.total_hours
        
        # Форматируем статистику проектов
        formatted_project_totals = {}
        for project_name, hours in project_totals.items():
            formatted_project_totals[project_name] = ProjectSummary(
                hours=round(hours, 1),
                formatted=format_duration(hours)
            )
        
        return DailySummary(
            period=period_str,
            active_days=active_days,
            total_time=format_duration(total_hours),
            project_totals=formatted_project_totals
        )
    
    def _calculate_project_summary(self, days_data: Dict[str, ProjectDayData], start_date: date, end_date: date) -> ProjectTimelineSummary:
        """Рассчитывает сводку для временной шкалы проекта"""
        active_days = len(days_data)
        period_str = f"{start_date.isoformat()} to {end_date.isoformat()}"
        
        total_hours = 0.0
        all_sessions = []
        
        for day_data in days_data.values():
            total_hours += day_data.total_hours
            for block in day_data.time_blocks:
                # Парсим длительность сессии
                duration_parts = block.duration.split(':')
                hours = int(duration_parts[0]) + int(duration_parts[1])/60 + int(duration_parts[2])/3600
                all_sessions.append(hours)
        
        # Рассчитываем средние значения
        avg_daily_hours = total_hours / max(active_days, 1)
        longest_session_hours = max(all_sessions) if all_sessions else 0
        avg_session_hours = sum(all_sessions) / len(all_sessions) if all_sessions else 0
        
        return ProjectTimelineSummary(
            period=period_str,
            active_days=active_days,
            total_time=format_duration(total_hours),
            avg_daily=format_duration(avg_daily_hours),
            longest_session=format_session_duration(longest_session_hours),
            avg_session=format_session_duration(avg_session_hours)
        )
