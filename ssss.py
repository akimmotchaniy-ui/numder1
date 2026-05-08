# ============================================================
# МОДУЛЬ ИНТЕГРАЦИИ PIWEB API ДЛЯ КИБЕРДЕК МАРКЕТПЛЕЙСА
# БИБЛИОТЕКА: piweb_api_client.py
# Версия: 1.0.0
# Назначение: Взаимодействие с PiWeb API для загрузки прошивок,
#              получения техданных, управления ESP32 устройствами
# ============================================================

import requests
import json
import hashlib
import time
import hmac
from typing import Optional, Dict, List, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin


# ============================================================
# КОНФИГУРАЦИЯ И ТИПЫ ДАННЫХ
# ============================================================

class PiWebEndpoint(Enum):
    """Эндпоинты PiWeb API"""
    FIRMWARE_LIST = "/api/v2/firmware/list"
    FIRMWARE_DOWNLOAD = "/api/v2/firmware/download"
    FIRMWARE_UPLOAD = "/api/v2/firmware/upload"
    DEVICE_INFO = "/api/v2/device/info"
    DEVICE_FLASH = "/api/v2/device/flash"
    ESP32_DATASHEET = "/api/v2/esp32/datasheet"
    COMPONENTS_SEARCH = "/api/v2/components/search"
    SCHEMATICS_GET = "/api/v2/schematics/get"
    PINOUT_VIEWER = "/api/v2/pinout/viewer"


@dataclass
class PiWebConfig:
    """Конфигурация подключения к PiWeb"""
    base_url: str = "https://api.piweb.io"
    api_key: str = ""
    api_secret: str = ""
    timeout: int = 30
    max_retries: int = 3
    verify_ssl: bool = True
    user_agent: str = "CyberDeckMarket/2.0 (ESP32-Firmware-Manager)"

    def __post_init__(self):
        if not self.api_key:
            raise ValueError("API ключ PiWeb обязателен")
        if not self.api_secret:
            raise ValueError("API секрет PiWeb обязателен")


@dataclass
class FirmwareInfo:
    """Информация о прошивке"""
    id: str
    name: str
    version: str
    description: str
    board_type: str  # ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6
    file_size_bytes: int
    md5_checksum: str
    sha256_checksum: str
    download_url: str
    created_at: str
    author: str
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ESP32DeviceInfo:
    """Информация об ESP32 устройстве"""
    chip_model: str
    chip_revision: int
    cpu_cores: int
    cpu_frequency_mhz: int
    flash_size_mb: int
    psram_size_mb: int
    sram_size_kb: int
    mac_address: str
    efuse_mac: str
    sdk_version: str
    free_heap_bytes: int
    temperature_celsius: float = 0.0  # ±0.1°C
    voltage_v: float = 3.3  # ±0.01V


# ============================================================
# ИСКЛЮЧЕНИЯ
# ============================================================

class PiWebException(Exception):
    """Базовое исключение PiWeb"""
    pass


class PiWebAuthError(PiWebException):
    """Ошибка аутентификации (HTTP 401)"""
    pass


class PiWebRateLimitError(PiWebException):
    """Превышен лимит запросов (HTTP 429)"""
    pass


class PiWebNotFoundError(PiWebException):
    """Ресурс не найден (HTTP 404)"""
    pass


class PiWebServerError(PiWebException):
    """Ошибка сервера (HTTP 5xx)"""
    pass


# ============================================================
# ОСНОВНОЙ КЛАСС PIWEB КЛИЕНТА
# ============================================================

class PiWebClient:
    """
    HTTP клиент для взаимодействия с PiWeb API.

    Поддерживает:
    - Аутентификацию HMAC-SHA256
    - Автоматический ретрай с экспоненциальной задержкой
    - Скачивание и загрузку прошивок для ESP32
    - Получение технической документации
    - Поиск компонентов и схем
    """

    def __init__(self, config: PiWebConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.user_agent,
            'Accept': 'application/json',
            'X-Api-Key': config.api_key
        })
        self.session.verify = config.verify_ssl

        # Кеш для снижения количества запросов
        self._firmware_cache: Dict[str, FirmwareInfo] = {}
        self._cache_ttl: int = 300  # 5 минут

    def _generate_signature(self, method: str, endpoint: str,
                            timestamp: int, body: str = "") -> str:
        """
        Генерация HMAC-SHA256 подписи для аутентификации.

        Алгоритм:
        signature = HMAC-SHA256(api_secret,
            method + "\n" + endpoint + "\n" + str(timestamp) + "\n" + body)
        """
        message = f"{method}\n{endpoint}\n{timestamp}\n{body}"
        signature = hmac.new(
            self.config.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _make_request(self, method: str, endpoint: str,
                      params: Optional[Dict] = None,
                      data: Optional[Dict] = None,
                      files: Optional[Dict] = None,
                      stream: bool = False) -> requests.Response:
        """
        Выполнение HTTP запроса с подписью и ретраями.

        Параметры:
        - method: HTTP метод (GET, POST, PUT, DELETE)
        - endpoint: путь API (из PiWebEndpoint)
        - params: query параметры
        - data: тело запроса (JSON)
        - files: файлы для загрузки
        - stream: потоковый режим для скачивания

        Возвращает:
        - requests.Response объект

        Исключения:
        - PiWebAuthError (401)
        - PiWebRateLimitError (429)
        - PiWebNotFoundError (404)
        - PiWebServerError (5xx)
        """
        url = urljoin(self.config.base_url, endpoint)
        timestamp = int(time.time())

        # Подготовка тела для подписи
        body_str = ""
        if data:
            body_str = json.dumps(data, sort_keys=True)

        # Генерация подписи
        signature = self._generate_signature(method, endpoint, timestamp, body_str)

        headers = {
            'X-Timestamp': str(timestamp),
            'X-Signature': signature,
            'Content-Type': 'application/json' if not files else None
        }
        if files:
            del headers['Content-Type']  # requests сам установит multipart

        # Ретрай логика с экспоненциальной задержкой
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data if not files else None,
                    data=None if not files else data,
                    files=files,
                    headers=headers,
                    timeout=self.config.timeout,
                    stream=stream
                )

                # Обработка HTTP ошибок
                if response.status_code == 401:
                    raise PiWebAuthError(f"Неверный API ключ: {response.text}")
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 404:
                    raise PiWebNotFoundError(f"Ресурс не найден: {url}")
                elif response.status_code >= 500:
                    if attempt < self.config.max_retries - 1:
                        time.sleep(2 ** attempt)  # Экспоненциальная задержка
                        continue
                    raise PiWebServerError(f"Ошибка сервера {response.status_code}: {response.text}")

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise PiWebException("Таймаут соединения с PiWeb API")

            except requests.exceptions.ConnectionError as e:
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise PiWebException(f"Ошибка соединения: {str(e)}")

        raise PiWebException(f"Не удалось выполнить запрос после {self.config.max_retries} попыток")

    # ============================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПРОШИВКАМИ
    # ============================================================

    def get_firmware_list(self, board_type: Optional[str] = None,
                          search: Optional[str] = None,
                          page: int = 1, per_page: int = 20) -> List[FirmwareInfo]:
        """
        Получение списка доступных прошивок.

        Параметры:
        - board_type: фильтр по типу платы (ESP32, ESP32-S3 и т.д.)
        - search: поиск по названию/описанию
        - page: номер страницы
        - per_page: элементов на странице

        Возвращает:
        - Список FirmwareInfo объектов
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        if board_type:
            params['board_type'] = board_type
        if search:
            params['q'] = search

        response = self._make_request(
            'GET',
            PiWebEndpoint.FIRMWARE_LIST.value,
            params=params
        )

        data = response.json()
        firmwares = []

        for item in data.get('firmwares', []):
            fw = FirmwareInfo(
                id=item['id'],
                name=item['name'],
                version=item['version'],
                description=item.get('description', ''),
                board_type=item['board_type'],
                file_size_bytes=item['file_size'],
                md5_checksum=item['md5'],
                sha256_checksum=item['sha256'],
                download_url=item['download_url'],
                created_at=item['created_at'],
                author=item.get('author', 'Unknown'),
                tags=item.get('tags', []),
                dependencies=item.get('dependencies', [])
            )
            firmwares.append(fw)

            # Обновление кеша
            self._firmware_cache[fw.id] = fw

        return firmwares

    def download_firmware(self, firmware_id: str,
                          save_path: str) -> str:
        """
        Скачивание прошивки на диск.

        Параметры:
        - firmware_id: ID прошивки
        - save_path: путь для сохранения файла

        Возвращает:
        - MD5 хеш скачанного файла

        Исключения:
        - PiWebNotFoundError: прошивка не найдена
        - PiWebException: ошибка проверки целостности
        """
        # Получаем информацию о прошивке
        if firmware_id not in self._firmware_cache:
            self.get_firmware_list()

        fw_info = self._firmware_cache.get(firmware_id)
        if not fw_info:
            raise PiWebNotFoundError(f"Прошивка {firmware_id} не найдена")

        # Скачивание
        response = self._make_request(
            'GET',
            f"{PiWebEndpoint.FIRMWARE_DOWNLOAD.value}/{firmware_id}",
            stream=True
        )

        # Потоковая запись на диск
        downloaded_md5 = hashlib.md5()
        total_bytes = 0

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_md5.update(chunk)
                    total_bytes += len(chunk)

        # Проверка целостности
        actual_md5 = downloaded_md5.hexdigest()
        if actual_md5 != fw_info.md5_checksum:
            import os
            os.remove(save_path)
            raise PiWebException(
                f"Ошибка целостности! Ожидался MD5: {fw_info.md5_checksum}, "
                f"получен: {actual_md5}"
            )

        # Проверка размера
        if total_bytes != fw_info.file_size_bytes:
            import os
            os.remove(save_path)
            raise PiWebException(
                f"Неверный размер файла! Ожидалось: {fw_info.file_size_bytes} байт, "
                f"получено: {total_bytes} байт"
            )

        return actual_md5

    def upload_firmware(self, name: str, version: str,
                        description: str, board_type: str,
                        file_path: str, tags: Optional[List[str]] = None) -> str:
        """
        Загрузка прошивки на PiWeb.

        Параметры:
        - name: название прошивки
        - version: версия (семантическое версионирование)
        - description: описание
        - board_type: тип платы ESP32
        - file_path: путь к бинарному файлу прошивки
        - tags: теги для категоризации

        Возвращает:
        - ID загруженной прошивки
        """
        # Вычисление хешей файла
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()
        file_size = 0

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)
                file_size += len(chunk)

        # Подготовка метаданных
        metadata = {
            'name': name,
            'version': version,
            'description': description,
            'board_type': board_type,
            'file_size': file_size,
            'md5': md5_hash.hexdigest(),
            'sha256': sha256_hash.hexdigest(),
            'tags': tags or []
        }

        # Загрузка файла
        with open(file_path, 'rb') as f:
            files = {
                'firmware': (f"{name}-{version}.bin", f, 'application/octet-stream')
            }
            data = {'metadata': json.dumps(metadata)}

            response = self._make_request(
                'POST',
                PiWebEndpoint.FIRMWARE_UPLOAD.value,
                data=data,
                files=files
            )

        result = response.json()
        return result['firmware_id']

    # ============================================================
    # МЕТОДЫ ДЛЯ ESP32 УСТРОЙСТВ
    # ============================================================

    def get_device_info(self, device_ip: str,
                        device_port: int = 80) -> ESP32DeviceInfo:
        """
        Получение информации об ESP32 устройстве через PiWeb API.

        Параметры:
        - device_ip: IP адрес устройства в локальной сети
        - device_port: HTTP порт устройства

        Возвращает:
        - ESP32DeviceInfo с детальной информацией
        """
        params = {
            'ip': device_ip,
            'port': device_port
        }

        response = self._make_request(
            'GET',
            PiWebEndpoint.DEVICE_INFO.value,
            params=params
        )

        data = response.json()
        device = ESP32DeviceInfo(
            chip_model=data['chip_model'],
            chip_revision=data['chip_revision'],
            cpu_cores=data['cpu_cores'],
            cpu_frequency_mhz=data['cpu_freq_mhz'],
            flash_size_mb=data['flash_size_mb'],
            psram_size_mb=data.get('psram_size_mb', 0),
            sram_size_kb=data['sram_size_kb'],
            mac_address=data['mac_address'],
            efuse_mac=data['efuse_mac'],
            sdk_version=data['sdk_version'],
            free_heap_bytes=data['free_heap_bytes'],
            temperature_celsius=data.get('temperature_celsius', 0.0),
            voltage_v=data.get('voltage_v', 3.3)
        )

        return device

    def flash_firmware_ota(self, device_ip: str, firmware_id: str,
                           device_port: int = 3232) -> bool:
        """
        Прошивка ESP32 устройства по воздуху (OTA).

        Параметры:
        - device_ip: IP адрес устройства
        - firmware_id: ID прошивки в PiWeb
        - device_port: OTA порт устройства (обычно 3232)

        Возвращает:
        - True если прошивка успешна

        Исключения:
        - PiWebException: ошибка прошивки
        """
        payload = {
            'device_ip': device_ip,
            'device_port': device_port,
            'firmware_id': firmware_id,
            'flash_timeout': 120  # Таймаут прошивки в секундах
        }

        response = self._make_request(
            'POST',
            PiWebEndpoint.DEVICE_FLASH.value,
            data=payload
        )

        result = response.json()

        if result['status'] != 'success':
            raise PiWebException(
                f"Ошибка прошивки устройства {device_ip}: {result.get('error', 'Неизвестная ошибка')}"
            )

        return True

    # ============================================================
    # МЕТОДЫ ДЛЯ ТЕХНИЧЕСКОЙ ДОКУМЕНТАЦИИ
    # ============================================================

    def get_esp32_datasheet(self, chip_model: str,
                            language: str = 'ru') -> str:
        """
        Получение даташита на ESP32 чип.

        Параметры:
        - chip_model: модель чипа (ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6)
        - language: язык даташита (ru, en, cn)

        Возвращает:
        - URL для скачивания PDF даташита
        """
        params = {
            'model': chip_model,
            'lang': language
        }

        response = self._make_request(
            'GET',
            PiWebEndpoint.ESP32_DATASHEET.value,
            params=params
        )

        return response.json()['datasheet_url']

    def search_components(self, query: str,
                          category: Optional[str] = None,
                          in_stock_only: bool = True) -> List[Dict]:
        """
        Поиск электронных компонентов через PiWeb.

        Параметры:
        - query: поисковый запрос
        - category: категория (resistors, capacitors, microcontrollers, sensors)
        - in_stock_only: только в наличии

        Возвращает:
        - Список компонентов с ценами и наличием
        """
        params = {
            'q': query,
            'in_stock': str(in_stock_only).lower()
        }
        if category:
            params['category'] = category

        response = self._make_request(
            'GET',
            PiWebEndpoint.COMPONENTS_SEARCH.value,
            params=params
        )

        return response.json().get('components', [])

    def get_pinout(self, board_model: str,
                   file_format: str = 'png') -> bytes:
        """
        Получение изображения распиновки платы.

        Параметры:
        - board_model: модель платы (ESP32-DevKitC, ESP32-S3-DevKitM и т.д.)
        - file_format: формат изображения (png, svg, pdf)

        Возвращает:
        - Бинарные данные изображения
        """
        params = {
            'model': board_model,
            'format': file_format
        }

        response = self._make_request(
            'GET',
            PiWebEndpoint.PINOUT_VIEWER.value,
            params=params
        )

        return response.content


# ============================================================
# ФАСАД ДЛЯ FLASK ПРИЛОЖЕНИЯ
# ============================================================

class PiWebFacade:
    """
    Фасад для интеграции PiWeb в Flask приложение CyberDeck Market.
    Предоставляет упрощенный интерфейс для работы с прошивками.
    """

    def __init__(self, app=None):
        self.client: Optional[PiWebClient] = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Инициализация с Flask приложением"""
        config = PiWebConfig(
            base_url=app.config.get('PIWEB_BASE_URL', 'https://api.piweb.io'),
            api_key=app.config.get('PIWEB_API_KEY', ''),
            api_secret=app.config.get('PIWEB_API_SECRET', ''),
            timeout=app.config.get('PIWEB_TIMEOUT', 30)
        )
        self.client = PiWebClient(config)

        # Сохранение в extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['piweb'] = self

    def sync_firmwares_to_db(self, db, ESP32Firmware):
        """
        Синхронизация прошивок из PiWeb в локальную БД.

        Параметры:
        - db: SQLAlchemy db объект
        - ESP32Firmware: модель ESP32Firmware
        """
        if not self.client:
            raise PiWebException("Клиент не инициализирован")

        # Получение всех прошивок
        firmwares = self.client.get_firmware_list(per_page=100)

        for fw in firmwares:
            existing = ESP32Firmware.query.filter_by(
                name=fw.name,
                version=fw.version
            ).first()

            if not existing:
                new_fw = ESP32Firmware(
                    name=fw.name,
                    version=fw.version,
                    description=fw.description,
                    file_size_kb=round(fw.file_size_bytes / 1024.0, 2),
                    md5_checksum=fw.md5_checksum,
                    board_type=fw.board_type
                )
                db.session.add(new_fw)

        db.session.commit()
        return len(firmwares)

    def download_and_store_firmware(self, firmware_id: str,
                                    db, ESP32Firmware) -> bytes:
        """
        Скачивание прошивки и сохранение в БД.

        Параметры:
        - firmware_id: ID прошивки в PiWeb
        - db: SQLAlchemy db объект
        - ESP32Firmware: модель ESP32Firmware

        Возвращает:
        - Бинарные данные прошивки
        """
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as tmp:
            temp_path = tmp.name

        try:
            # Скачивание
            self.client.download_firmware(firmware_id, temp_path)

            # Чтение в память
            with open(temp_path, 'rb') as f:
                binary_data = f.read()

            # Обновление записи в БД
            fw_info = self.client._firmware_cache.get(firmware_id)
            if fw_info:
                firmware = ESP32Firmware.query.filter_by(
                    name=fw_info.name,
                    version=fw_info.version
                ).first()

                if firmware:
                    firmware.binary_data = binary_data
                    firmware.file_size_kb = round(len(binary_data) / 1024.0, 2)
                    db.session.commit()

            return binary_data

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


# ============================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ В FLASK ПРИЛОЖЕНИИ
# ============================================================

"""
# В файле app.py или __init__.py:

from piweb_api_client import PiWebFacade, PiWebConfig

# Создание фасада
piweb = PiWebFacade()

def create_app():
    app = Flask(__name__)

    # Конфигурация
    app.config['PIWEB_API_KEY'] = 'ваш_api_ключ'
    app.config['PIWEB_API_SECRET'] = 'ваш_api_секрет'
    app.config['PIWEB_BASE_URL'] = 'https://api.piweb.io'

    # Инициализация
    piweb.init_app(app)

    # Маршрут для списка прошивок
    @app.route('/firmware')
    def firmware_list():
        board_type = request.args.get('board', 'ESP32')
        search = request.args.get('q', '')

        try:
            firmwares = piweb.client.get_firmware_list(
                board_type=board_type,
                search=search
            )
        except PiWebException as e:
            flash(f'Ошибка PiWeb API: {str(e)}', 'danger')
            firmwares = []

        return render_template('firmware_list.html', firmwares=firmwares)

    # Маршрут для скачивания прошивки
    @app.route('/firmware/download/<firmware_id>')
    @login_required
    def firmware_download(firmware_id):
        import tempfile
        import os

        temp_path = None
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.bin')
            os.close(temp_fd)

            md5 = piweb.client.download_firmware(firmware_id, temp_path)

            return send_file(
                temp_path,
                as_attachment=True,
                download_name=f'firmware_{firmware_id}.bin',
                mimetype='application/octet-stream'
            )
        except PiWebException as e:
            flash(f'Ошибка скачивания: {str(e)}', 'danger')
            return redirect(url_for('firmware_list'))
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    # Маршрут для OTA прошивки
    @app.route('/device/flash', methods=['POST'])
    @login_required
    @admin_required
    def device_flash_ota():
        device_ip = request.form.get('device_ip', '')
        firmware_id = request.form.get('firmware_id', '')

        try:
            success = piweb.client.flash_firmware_ota(device_ip, firmware_id)
            if success:
                flash(f'Устройство {device_ip} успешно прошито!', 'success')
        except PiWebException as e:
            flash(f'Ошибка OTA прошивки: {str(e)}', 'danger')

        return redirect(url_for('device_management'))

    # Маршрут для информации об устройстве
    @app.route('/device/info/<ip>')
    @login_required
    def device_info(ip):
        try:
            info = piweb.client.get_device_info(ip)
            return jsonify({
                'chip': info.chip_model,
                'cores': info.cpu_cores,
                'freq_mhz': info.cpu_frequency_mhz,
                'flash_mb': info.flash_size_mb,
                'sram_kb': info.sram_size_kb,
                'psram_mb': info.psram_size_mb,
                'mac': info.mac_address,
                'temp_c': info.temperature_celsius,
                'voltage': info.voltage_v,
                'free_heap': info.free_heap_bytes
            })
        except PiWebException as e:
            return jsonify({'error': str(e)}), 500

    return app
"""

# ============================================================
# ТЕСТОВЫЙ МОДУЛЬ
# ============================================================

if __name__ == '__main__':
    """
    Тестирование PiWeb клиента.
    Запуск: python piweb_api_client.py
    """
    import sys

    # Тестовая конфигурация
    test_config = PiWebConfig(
        base_url="https://api.piweb.io",
        api_key="test_key_12345",
        api_secret="test_secret_abcdef",
        verify_ssl=False  # Для тестирования
    )

    try:
        client = PiWebClient(test_config)

        # Тест получения списка прошивок
        print("=" * 60)
        print("ТЕСТ 1: Получение списка прошивок для ESP32-S3")
        print("=" * 60)

        firmwares = client.get_firmware_list(board_type="ESP32-S3", per_page=5)
        for fw in firmwares:
            print(f"  - {fw.name} v{fw.version} ({fw.board_type})")
            print(f"    Размер: {fw.file_size_bytes / 1024:.2f} КБ")
            print(f"    MD5: {fw.md5_checksum}")

        # Тест поиска компонентов
        print("\n" + "=" * 60)
        print("ТЕСТ 2: Поиск компонентов")
        print("=" * 60)

        components = client.search_components("ESP32-WROOM", in_stock_only=True)
        for comp in components[:3]:
            print(f"  - {comp.get('name')}: ${comp.get('price_usd')} ({comp.get('stock')} шт.)")

        # Тест получения даташита
        print("\n" + "=" * 60)
        print("ТЕСТ 3: Получение даташита")
        print("=" * 60)

        datasheet_url = client.get_esp32_datasheet("ESP32-S3", language="ru")
        print(f"  URL даташита: {datasheet_url}")

        # Тест получения распиновки
        print("\n" + "=" * 60)
        print("ТЕСТ 4: Получение распиновки")
        print("=" * 60)

        pinout_data = client.get_pinout("ESP32-DevKitC", file_format="png")
        print(f"  Размер изображения: {len(pinout_data)} байт")

        # Тест информации об устройстве
        print("\n" + "=" * 60)
        print("ТЕСТ 5: Информация об устройстве")
        print("=" * 60)

        device = client.get_device_info("192.168.1.100")
        print(f"  Чип: {device.chip_model} rev.{device.chip_revision}")
        print(f"  CPU: {device.cpu_cores} ядер @ {device.cpu_frequency_mhz} МГц")
        print(f"  Flash: {device.flash_size_mb} МБ, PSRAM: {device.psram_size_mb} МБ")
        print(f"  MAC: {device.mac_address}")
        print(f"  Температура: {device.temperature_celsius}°C")
        print(f"  Напряжение: {device.voltage_v}V")
        print(f"  Свободно кучи: {device.free_heap_bytes} байт")

        print("\n[OK] Все тесты пройдены успешно!")

    except PiWebAuthError:
        print("[ERROR] Ошибка аутентификации. Проверьте API ключ и секрет.", file=sys.stderr)
        sys.exit(1)
    except PiWebException as e:
        print(f"[ERROR] Ошибка PiWeb: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Неожиданная ошибка: {str(e)}", file=sys.stderr)
        sys.exit(1)