import json

# Читаем данные из файла репозитория
with open('filters.json', 'r') as f:
    repo_filters = json.load(f)

# Читаем данные с сервера (если файла нет, используем пустой словарь)
try:
    with open('server_filters.json', 'r') as f:
        server_filters = json.load(f)
except FileNotFoundError:
    server_filters = {
        "bw": [],
        "lw": [],
        "ban": [],
        "price": 0,
        "delay": 0
    }

# Объединяем списки bw, lw, ban, исключая дубликаты
for key in ["bw", "lw", "ban"]:
    combined_set = set(server_filters.get(key, [])) | set(repo_filters.get(key, []))
    server_filters[key] = list(combined_set)

# Обновляем price и delay, беря максимальное значение
server_filters["price"] = max(server_filters.get("price", 0), repo_filters.get("price", 0))
server_filters["delay"] = max(server_filters.get("delay", 0), repo_filters.get("delay", 0))

# Записываем результат обратно в server_filters.json
with open('server_filters.json', 'w') as f:
    json.dump(server_filters, f, ensure_ascii=False, indent=2)
