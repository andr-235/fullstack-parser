 

echo "Тестирование функционала статуса комментариев..."

# Получаем список комментариев
echo "1. Получение списка комментариев..."
COMMENTS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/parser/comments/?size=5")
echo "Найдено комментариев: $(echo $COMMENTS_RESPONSE | jq '.total')"

# Получаем ID первого комментария
FIRST_COMMENT_ID=$(echo $COMMENTS_RESPONSE | jq '.items[0].id')
echo "ID первого комментария: $FIRST_COMMENT_ID"

if [ "$FIRST_COMMENT_ID" != "null" ] && [ "$FIRST_COMMENT_ID" != "" ]; then
    # Отмечаем как просмотренный
    echo "2. Отмечаем комментарий как просмотренный..."
    VIEWED_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/parser/comments/$FIRST_COMMENT_ID/view")
    echo "Статус после отметки как просмотренный: $(echo $VIEWED_RESPONSE | jq '.is_viewed')"
    
    # Архивируем комментарий
    echo "3. Архивируем комментарий..."
    ARCHIVED_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/parser/comments/$FIRST_COMMENT_ID/archive")
    echo "Статус после архивирования: $(echo $ARCHIVED_RESPONSE | jq '.is_archived')"
    
    # Разархивируем комментарий
    echo "4. Разархивируем комментарий..."
    UNARCHIVED_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/parser/comments/$FIRST_COMMENT_ID/unarchive")
    echo "Статус после разархивирования: $(echo $UNARCHIVED_RESPONSE | jq '.is_archived')"
    
    # Тестируем фильтрацию
    echo "5. Тестируем фильтрацию по просмотренным комментариям..."
    VIEWED_FILTER_RESPONSE=$(curl -s "http://localhost:8000/api/v1/parser/comments/?is_viewed=true&size=5")
    echo "Найдено просмотренных комментариев: $(echo $VIEWED_FILTER_RESPONSE | jq '.total')"
    
    echo "6. Тестируем фильтрацию по не просмотренным комментариям..."
    UNVIEWED_FILTER_RESPONSE=$(curl -s "http://localhost:8000/api/v1/parser/comments/?is_viewed=false&size=5")
    echo "Найдено не просмотренных комментариев: $(echo $UNVIEWED_FILTER_RESPONSE | jq '.total')"
    
    echo "✅ Тестирование завершено успешно!"
else
    echo "❌ Не удалось найти комментарии для тестирования"
fi