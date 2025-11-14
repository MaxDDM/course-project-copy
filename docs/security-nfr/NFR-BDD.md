<p> Для NFR-01:

Feature: Производительность получения тренировок
  Scenario: p95 времени ответа на GET /workouts в рамках порога
    Given: сервис deployed на stage среде
    When: выполняется нагрузочный тест с 50 RPS в течение 5 минут
    Then: p95 времени ответа на GET /workouts ≤ 250 ms</p>
<p> Для NFR-02:

Feature: Создание тренировки
Scenario: Успешность создания тренировки
    Given: сервис deployed на stage среде
    When: выполняются последовательные POST /workouts
    Then: доля успешных ответов ≥ 99%</p>
<p> Для NFR-03:

Feature: Корректность привязки Set к тренировке
Scenario: Привязка Set к существующей тренировке
    Given: существующая тренировка
    When: выполняется POST /workouts/{id}/sets с валидным payload
    Then: ответ 201 и Set создан</p>
