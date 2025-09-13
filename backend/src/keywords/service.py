"""
Сервис для работы с ключевыми словами
"""

import json
import csv
import io
from typing import List, Optional, Dict, Any
from datetime import datetime

from shared.presentation.exceptions import ValidationException as ValidationError
from keywords.models import KeywordsRepository, Keyword


class KeywordsService:
    """Сервис для работы с ключевыми словами"""
    
    def __init__(self, repository: KeywordsRepository):
        self.repository = repository
    
    async def create_keyword(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать ключевое слово"""
        self._validate_keyword_data(data)
        
        # Проверка на дубликаты
        existing = await self.repository.get_by_word(data["word"])
        if existing:
            raise ValidationError("Ключевое слово уже существует", field="word")
        
        keyword = await self.repository.create(data)
        return keyword.to_dict()
    
    async def get_keyword(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """Получить ключевое слово по ID"""
        keyword = await self.repository.get_by_id(keyword_id)
        return keyword.to_dict() if keyword else None
    
    async def get_keywords(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        **filters
    ) -> Dict[str, Any]:
        """Получить список ключевых слов с фильтрами"""
        keywords = await self.repository.get_all(
            active_only=active_only,
            category=category,
            search=search,
            limit=limit,
            offset=offset
        )
        
        # Применяем дополнительные фильтры
        filtered_keywords = self._apply_filters(keywords, **filters)
        
        # Пагинация
        total = len(filtered_keywords)
        page = (offset // limit) + 1 if limit > 0 else 1
        pages = (total + limit - 1) // limit if limit > 0 else 0
        
        return {
            "items": [kw.to_dict() for kw in filtered_keywords],
            "total": total,
            "page": page,
            "size": limit,
            "pages": pages,
        }
    
    async def update_keyword(self, keyword_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновить ключевое слово"""
        # Валидация данных обновления
        if "word" in data:
            self._validate_keyword_data({"word": data["word"]})
            
            # Проверка на дубликаты
            existing = await self.repository.get_by_word(data["word"])
            if existing and existing.id != keyword_id:
                raise ValidationError("Ключевое слово уже существует", field="word")
        
        success = await self.repository.update(keyword_id, data)
        if success:
            keyword = await self.repository.get_by_id(keyword_id)
            return keyword.to_dict() if keyword else None
        return None
    
    async def delete_keyword(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        return await self.repository.delete(keyword_id)
    
    async def activate_keyword(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """Активировать ключевое слово"""
        keyword = await self.repository.get_by_id(keyword_id)
        if not keyword:
            return None
        
        if keyword.is_archived:
            raise ValidationError("Нельзя активировать архивированное ключевое слово")
        
        success = await self.repository.update(keyword_id, {
            "is_active": True,
            "is_archived": False,
            "updated_at": datetime.utcnow()
        })
        
        if success:
            keyword = await self.repository.get_by_id(keyword_id)
            return keyword.to_dict() if keyword else None
        return None
    
    async def deactivate_keyword(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """Деактивировать ключевое слово"""
        success = await self.repository.update(keyword_id, {
            "is_active": False,
            "is_archived": False,
            "updated_at": datetime.utcnow()
        })
        
        if success:
            keyword = await self.repository.get_by_id(keyword_id)
            return keyword.to_dict() if keyword else None
        return None
    
    async def archive_keyword(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """Архивировать ключевое слово"""
        success = await self.repository.update(keyword_id, {
            "is_active": False,
            "is_archived": True,
            "updated_at": datetime.utcnow()
        })
        
        if success:
            keyword = await self.repository.get_by_id(keyword_id)
            return keyword.to_dict() if keyword else None
        return None
    
    async def bulk_create_keywords(self, keywords_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Массовое создание ключевых слов"""
        if len(keywords_data) > 100:
            raise ValidationError("Максимум 100 ключевых слов за один запрос")
        
        successful = 0
        failed = 0
        errors = []
        
        for i, data in enumerate(keywords_data):
            try:
                self._validate_keyword_data(data)
                await self.repository.create(data)
                successful += 1
            except Exception as e:
                failed += 1
                errors.append({
                    "index": i,
                    "word": data.get("word", "unknown"),
                    "error": str(e),
                })
        
        return {
            "total_requested": len(keywords_data),
            "successful": successful,
            "failed": failed,
            "errors": errors,
        }
    
    async def bulk_action(self, keyword_ids: List[int], action: str) -> Dict[str, Any]:
        """Массовая операция с ключевыми словами"""
        if action not in ["activate", "deactivate", "archive", "delete"]:
            raise ValidationError(f"Недопустимое действие: {action}")
        
        successful = 0
        failed = 0
        errors = []
        
        for keyword_id in keyword_ids:
            try:
                if action == "activate":
                    result = await self.activate_keyword(keyword_id)
                elif action == "deactivate":
                    result = await self.deactivate_keyword(keyword_id)
                elif action == "archive":
                    result = await self.archive_keyword(keyword_id)
                elif action == "delete":
                    success = await self.delete_keyword(keyword_id)
                    result = await self.get_keyword(keyword_id) if success else None
                
                if result is not None:
                    successful += 1
                else:
                    failed += 1
                    errors.append({
                        "keyword_id": keyword_id,
                        "error": "Ключевое слово не найдено",
                    })
            except Exception as e:
                failed += 1
                errors.append({
                    "keyword_id": keyword_id,
                    "error": str(e),
                })
        
        return {
            "total_requested": len(keyword_ids),
            "successful": successful,
            "failed": failed,
            "errors": errors,
        }
    
    async def search_keywords(self, query: str, **filters) -> List[Dict[str, Any]]:
        """Поиск ключевых слов"""
        keywords = await self.repository.get_all(search=query, **filters)
        return [kw.to_dict() for kw in keywords]
    
    async def get_categories(self) -> List[str]:
        """Получить список категорий"""
        return await self.repository.get_categories()
    
    async def get_categories_with_stats(self) -> List[Dict[str, Any]]:
        """Получить категории со статистикой"""
        keywords = await self.repository.get_all(active_only=False)
        
        category_stats = {}
        for keyword in keywords:
            if keyword.category_name:
                cat_name = keyword.category_name
                if cat_name not in category_stats:
                    category_stats[cat_name] = {
                        "category_name": cat_name,
                        "keyword_count": 0,
                        "active_count": 0,
                        "total_matches": 0,
                    }
                
                category_stats[cat_name]["keyword_count"] += 1
                if keyword.is_active:
                    category_stats[cat_name]["active_count"] += 1
                category_stats[cat_name]["total_matches"] += keyword.match_count
        
        return list(category_stats.values())
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        return await self.repository.get_stats()
    
    async def export_keywords(self, format_type: str = "json", **filters) -> Dict[str, Any]:
        """Экспорт ключевых слов"""
        if format_type not in ["json", "csv", "txt"]:
            raise ValidationError(f"Недопустимый формат экспорта: {format_type}")
        
        result = await self.get_keywords(**filters)
        keywords = result["items"]
        
        if format_type == "json":
            export_data = json.dumps(keywords, indent=2, default=str, ensure_ascii=False)
            filename = "keywords_export.json"
        elif format_type == "csv":
            export_data = self._export_to_csv(keywords)
            filename = "keywords_export.csv"
        else:  # txt
            export_data = self._export_to_txt(keywords)
            filename = "keywords_export.txt"
        
        return {
            "export_data": export_data,
            "format": format_type,
            "total_exported": len(keywords),
            "filename": filename,
        }
    
    async def import_keywords(self, import_data: str, update_existing: bool = False) -> Dict[str, Any]:
        """Импорт ключевых слов"""
        try:
            keywords_data = json.loads(import_data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Неверный формат JSON: {str(e)}")
        
        if not isinstance(keywords_data, list):
            raise ValidationError("Данные должны быть списком ключевых слов")
        
        successful = 0
        failed = 0
        updated = 0
        errors = []
        
        for i, data in enumerate(keywords_data):
            try:
                word = data.get("word")
                if not word:
                    raise ValidationError("Отсутствует поле 'word'")
                
                existing = await self.repository.get_by_word(word)
                if existing:
                    if update_existing:
                        await self.repository.update(existing.id, data)
                        updated += 1
                    else:
                        raise ValidationError(f"Ключевое слово '{word}' уже существует")
                else:
                    await self.repository.create(data)
                    successful += 1
                    
            except Exception as e:
                failed += 1
                errors.append({
                    "index": i,
                    "word": data.get("word", "unknown"),
                    "error": str(e),
                })
        
        return {
            "total_imported": len(keywords_data),
            "successful": successful,
            "updated": updated,
            "failed": failed,
            "errors": errors,
        }
    
    async def validate_keywords(self, words: List[str]) -> Dict[str, Any]:
        """Валидация списка слов"""
        valid_keywords = []
        invalid_keywords = []
        suggestions = {}
        
        for word in words:
            is_valid, error = self._validate_keyword_word(word)
            if is_valid:
                valid_keywords.append(word)
            else:
                invalid_keywords.append(word)
                suggestions[word] = [f"Исправьте: {error}"]
        
        return {
            "valid_keywords": valid_keywords,
            "invalid_keywords": invalid_keywords,
            "suggestions": suggestions,
        }
    
    def _validate_keyword_data(self, data: Dict[str, Any]) -> None:
        """Валидация данных ключевого слова"""
        if not data.get("word"):
            raise ValidationError("Ключевое слово обязательно", field="word")
        
        if len(data["word"]) > 255:
            raise ValidationError("Ключевое слово слишком длинное (макс 255 символов)", field="word")
        
        if data.get("description") and len(data["description"]) > 1000:
            raise ValidationError("Описание слишком длинное (макс 1000 символов)", field="description")
        
        if data.get("category_name") and len(data["category_name"]) > 100:
            raise ValidationError("Название категории слишком длинное (макс 100 символов)", field="category_name")
        
        priority = data.get("priority", 5)
        if not (1 <= priority <= 10):
            raise ValidationError("Приоритет должен быть от 1 до 10", field="priority")
    
    def _validate_keyword_word(self, word: str) -> tuple[bool, str]:
        """Валидация отдельного слова"""
        if not word or not word.strip():
            return False, "Слово не может быть пустым"
        
        word = word.strip()
        if len(word) > 255:
            return False, "Слово слишком длинное (макс 255 символов)"
        
        if not word.replace(" ", "").replace("-", "").replace("_", "").isalnum():
            return False, "Слово содержит недопустимые символы"
        
        return True, ""
    
    def _apply_filters(self, keywords: List[Keyword], **filters) -> List[Keyword]:
        """Применение дополнительных фильтров"""
        filtered = keywords
        
        if "priority_min" in filters:
            filtered = [k for k in filtered if k.priority >= filters["priority_min"]]
        
        if "priority_max" in filters:
            filtered = [k for k in filtered if k.priority <= filters["priority_max"]]
        
        if "match_count_min" in filters:
            filtered = [k for k in filtered if k.match_count >= filters["match_count_min"]]
        
        if "match_count_max" in filters:
            filtered = [k for k in filtered if k.match_count <= filters["match_count_max"]]
        
        return filtered
    
    def _export_to_csv(self, keywords: List[Dict[str, Any]]) -> str:
        """Экспорт в CSV формат"""
        if not keywords:
            return ""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = ["id", "word", "category", "description", "priority", "is_active", "match_count", "created_at"]
        writer.writerow(headers)
        
        for keyword in keywords:
            row = [
                keyword.get("id"),
                keyword.get("word"),
                keyword.get("category", {}).get("name", "") if keyword.get("category") else "",
                keyword.get("description", ""),
                keyword.get("priority"),
                keyword.get("status", {}).get("is_active"),
                keyword.get("match_count"),
                keyword.get("created_at"),
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    def _export_to_txt(self, keywords: List[Dict[str, Any]]) -> str:
        """Экспорт в текстовый формат"""
        if not keywords:
            return ""
        
        lines = []
        for keyword in keywords:
            category = keyword.get("category", {}).get("name", "без категории") if keyword.get("category") else "без категории"
            line = f"{keyword['word']} [{category}] - {keyword.get('description', 'без описания')}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def parse_csv_keywords(self, content: str) -> List[Dict[str, Any]]:
        """Парсинг CSV файла с ключевыми словами"""
        keywords = []
        reader = csv.DictReader(io.StringIO(content))
        
        for row in reader:
            keyword = {
                "word": row.get("word", "").strip(),
                "description": row.get("description", "").strip() or None,
                "category_name": row.get("category", "").strip() or None,
                "priority": int(row.get("priority", 5)),
            }
            
            if keyword["word"]:
                keywords.append(keyword)
        
        return keywords
    
    def parse_txt_keywords(self, content: str) -> List[Dict[str, Any]]:
        """Парсинг TXT файла с ключевыми словами"""
        keywords = []
        lines = content.strip().split("\n")
        
        for line in lines:
            word = line.strip()
            if word and not word.startswith("#"):
                keywords.append({
                    "word": word,
                    "description": None,
                    "category_name": None,
                    "priority": 5,
                })
        
        return keywords