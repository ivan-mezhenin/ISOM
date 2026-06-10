

## Сборка C-версии

```bash
cd ISOM_C && make
```

## Запуск

```bash
# Встроенные тесты
./ISOM_C/isom

# CLI
./ISOM_C/isom "P1(a,b)&P1(b,c)" "P1(x,y)&P1(y,z)"

# Чтение из файлов
./ISOM_C/isom @g1.txt @g2.txt

# Python
python3 ISOM_PYTHON/main.py "P1(a,b)&P1(b,c)" "P1(x,y)&P1(y,z)"
```

## Бенчмарк

```bash
python3 benchmark.py
```

Сравнивает C и Python на 5 сценариях, показывает ошибки Python-реализации, тестирует С до 10000 рёбер (2-арные и 4-арные предикаты).

