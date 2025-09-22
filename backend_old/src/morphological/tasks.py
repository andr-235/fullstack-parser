"""
Задачи морфологического анализа
"""

import json
from typing import Any, Dict, List, Optional

from celery import Task
from celery.exceptions import Retry

from ..common.celery_config import celery_app
from ..common.logging import get_logger
from ..common.redis_client import redis_client

logger = get_logger(__name__)


class MorphologicalTask(Task):
    """Базовый класс для задач морфологического анализа"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Обработчик успешного выполнения"""
        logger.info(
            f"Morphological task {self.name} completed successfully",
            task_id=task_id,
            args=args,
            kwargs=kwargs
        )
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработчик ошибки выполнения"""
        logger.error(
            f"Morphological task {self.name} failed",
            task_id=task_id,
            args=args,
            kwargs=kwargs,
            error=str(exc),
            traceback=str(einfo)
        )


@celery_app.task(
    bind=True,
    base=MorphologicalTask,
    name="morphological.analyze_text",
    queue="default",
    max_retries=3,
    default_retry_delay=30
)
def analyze_text_task(
    self,
    text: str,
    text_id: Optional[str] = None,
    analysis_type: str = "full"
) -> Dict[str, Any]:
    """Задача анализа текста"""
    try:
        logger.info(f"Starting morphological analysis for text: {text[:50]}...")
        
        # Здесь должна быть логика морфологического анализа
        # Например, через pymorphy2, spaCy, NLTK и т.д.
        
        # Имитация анализа
        analysis_result = {
            "text": text,
            "text_id": text_id,
            "analysis_type": analysis_type,
            "words": [],
            "sentences": [],
            "lemmas": [],
            "pos_tags": [],
            "sentiment": "neutral",
            "language": "ru",
            "confidence": 0.85,
            "processed_at": self.request.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
        # Простой анализ слов
        words = text.split()
        for i, word in enumerate(words):
            word_analysis = {
                "index": i,
                "word": word,
                "lemma": word.lower(),
                "pos": "NOUN" if word[0].isupper() else "VERB",
                "grammar": {
                    "case": "nom",
                    "number": "sing",
                    "gender": "masc"
                }
            }
            analysis_result["words"].append(word_analysis)
            analysis_result["lemmas"].append(word_analysis["lemma"])
            analysis_result["pos_tags"].append(word_analysis["pos"])
        
        # Анализ предложений
        sentences = text.split('.')
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                sentence_analysis = {
                    "index": i,
                    "text": sentence.strip(),
                    "word_count": len(sentence.split()),
                    "sentiment": "positive" if "хорошо" in sentence.lower() else "neutral"
                }
                analysis_result["sentences"].append(sentence_analysis)
        
        # Сохраняем результат в Redis
        if text_id:
            redis_client.set_json(
                f"morphological_analysis:{text_id}",
                analysis_result,
                ttl=86400  # 24 часа
            )
        
        logger.info(
            f"Morphological analysis completed",
            text_id=text_id,
            words_count=len(analysis_result["words"]),
            sentences_count=len(analysis_result["sentences"])
        )
        
        return {
            "status": "success",
            "text_id": text_id,
            "words_count": len(analysis_result["words"]),
            "sentences_count": len(analysis_result["sentences"]),
            "analysis_result": analysis_result,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Morphological analysis failed: {e}")
        raise self.retry(exc=e, countdown=30)


@celery_app.task(
    bind=True,
    base=MorphologicalTask,
    name="morphological.analyze_batch",
    queue="default",
    max_retries=3,
    default_retry_delay=60
)
def analyze_batch_task(
    self,
    texts: List[Dict[str, Any]],
    analysis_type: str = "full"
) -> Dict[str, Any]:
    """Задача пакетного анализа текстов"""
    try:
        logger.info(f"Starting batch morphological analysis for {len(texts)} texts")
        
        results = []
        for text_data in texts:
            try:
                text = text_data.get("text", "")
                text_id = text_data.get("id")
                
                # Анализируем текст
                analysis_result = analyze_text_task.delay(
                    text=text,
                    text_id=text_id,
                    analysis_type=analysis_type
                )
                
                result = analysis_result.get(timeout=60)
                results.append({
                    "text_id": text_id,
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"Failed to analyze text {text_data.get('id', 'unknown')}: {e}")
                results.append({
                    "text_id": text_data.get("id"),
                    "status": "failed",
                    "error": str(e)
                })
        
        successful = len([r for r in results if r["status"] == "success"])
        
        logger.info(
            f"Batch morphological analysis completed",
            total_texts=len(texts),
            successful=successful,
            failed=len(texts) - successful
        )
        
        return {
            "status": "completed",
            "total_texts": len(texts),
            "successful": successful,
            "failed": len(texts) - successful,
            "results": results,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Batch morphological analysis failed: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=MorphologicalTask,
    name="morphological.extract_keywords",
    queue="default",
    max_retries=3,
    default_retry_delay=30
)
def extract_keywords_task(
    self,
    text: str,
    text_id: Optional[str] = None,
    max_keywords: int = 10
) -> Dict[str, Any]:
    """Задача извлечения ключевых слов"""
    try:
        logger.info(f"Extracting keywords from text: {text[:50]}...")
        
        # Здесь должна быть логика извлечения ключевых слов
        # Например, через TF-IDF, TextRank, YAKE и т.д.
        
        # Имитация извлечения ключевых слов
        words = text.lower().split()
        word_freq = {}
        for word in words:
            # Простая фильтрация
            if len(word) > 3 and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Сортируем по частоте
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        keywords = []
        for word, freq in sorted_words[:max_keywords]:
            keywords.append({
                "word": word,
                "frequency": freq,
                "score": freq / len(words),
                "position": words.index(word) if word in words else -1
            })
        
        result = {
            "text": text,
            "text_id": text_id,
            "keywords": keywords,
            "total_words": len(words),
            "unique_words": len(word_freq),
            "extracted_at": self.request.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
        # Сохраняем результат в Redis
        if text_id:
            redis_client.set_json(
                f"keywords_extraction:{text_id}",
                result,
                ttl=86400  # 24 часа
            )
        
        logger.info(
            f"Keywords extraction completed",
            text_id=text_id,
            keywords_count=len(keywords)
        )
        
        return {
            "status": "success",
            "text_id": text_id,
            "keywords_count": len(keywords),
            "result": result,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Keywords extraction failed: {e}")
        raise self.retry(exc=e, countdown=30)


@celery_app.task(
    bind=True,
    base=MorphologicalTask,
    name="morphological.analyze_sentiment",
    queue="default",
    max_retries=3,
    default_retry_delay=30
)
def analyze_sentiment_task(
    self,
    text: str,
    text_id: Optional[str] = None
) -> Dict[str, Any]:
    """Задача анализа тональности"""
    try:
        logger.info(f"Analyzing sentiment for text: {text[:50]}...")
        
        # Здесь должна быть логика анализа тональности
        # Например, через предобученные модели, VADER, TextBlob и т.д.
        
        # Простой анализ тональности
        positive_words = ["хорошо", "отлично", "прекрасно", "замечательно", "супер"]
        negative_words = ["плохо", "ужасно", "отвратительно", "кошмар", "ужас"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        result = {
            "text": text,
            "text_id": text_id,
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "analyzed_at": self.request.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
        # Сохраняем результат в Redis
        if text_id:
            redis_client.set_json(
                f"sentiment_analysis:{text_id}",
                result,
                ttl=86400  # 24 часа
            )
        
        logger.info(
            f"Sentiment analysis completed",
            text_id=text_id,
            sentiment=sentiment,
            confidence=confidence
        )
        
        return {
            "status": "success",
            "text_id": text_id,
            "sentiment": sentiment,
            "confidence": confidence,
            "result": result,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise self.retry(exc=e, countdown=30)


@celery_app.task(
    bind=True,
    base=MorphologicalTask,
    name="morphological.cleanup_old_analysis",
    queue="low_priority",
    max_retries=3,
    default_retry_delay=60
)
def cleanup_old_analysis_task(
    self,
    days_old: int = 7
) -> Dict[str, Any]:
    """Задача очистки старых результатов анализа"""
    try:
        logger.info(f"Cleaning up analysis results older than {days_old} days")
        
        # Паттерны для поиска старых результатов
        patterns = [
            "morphological_analysis:*",
            "keywords_extraction:*",
            "sentiment_analysis:*"
        ]
        
        total_cleaned = 0
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            for key in keys:
                # Проверяем возраст данных
                ttl = redis_client.ttl(key)
                if ttl > days_old * 86400:  # Конвертируем дни в секунды
                    redis_client.delete(key)
                    total_cleaned += 1
        
        logger.info(
            f"Analysis cleanup completed",
            days_old=days_old,
            keys_cleaned=total_cleaned
        )
        
        return {
            "status": "completed",
            "days_old": days_old,
            "keys_cleaned": total_cleaned,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Analysis cleanup failed: {e}")
        raise self.retry(exc=e, countdown=60)
