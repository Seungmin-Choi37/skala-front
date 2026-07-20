import asyncio
import time
from typing import Optional
import httpx
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

# ===================================================================
# 1) Pydantic v2 스키마 정의 (타입 및 범위 검증 규칙 설정)
# ===================================================================

class WeatherRecord(BaseModel):
    """Open-Meteo 날씨 데이터 검증 모델"""
    latitude: float
    longitude: float
    timezone: str
    hourly_temperatures_count: int = Field(..., gt=0)  # 0 초과 범위 검증 조건

class CountryRecord(BaseModel):
    """Countries.dev 국가 정보 검증 모델"""
    name: str = Field(..., min_length=1)
    capital: str = Field(..., min_length=1)
    currency: Optional[str] = None  # API 응답에서 값이 없을 수 있으므로 None(Optional) 허용

class IPRecord(BaseModel):
    """IP-API 지역 정보 검증 모델"""
    ip: str = Field(..., min_length=1)
    country: str = Field(..., min_length=1)
    city: Optional[str] = None


# ===================================================================
# 2) 개별 API 비동기 수집 함수 정의 (httpx.AsyncClient 활용)
# ===================================================================

async def fetch_weather(client: httpx.AsyncClient):
    """Open-Meteo 서울 3일 시간대별 기온·강수확률 데이터 수집"""
    url = "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul"
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    data = response.json()
    return {
        "source": "Open-Meteo",
        "raw": {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "hourly_temperatures_count": len(data.get("hourly", {}).get("temperature_2m", []))
        }
    }

async def fetch_country(client: httpx.AsyncClient):
    """Countries.dev 한국 국가 정보 수집"""
    url = "https://countries.dev/alpha/KOR"
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    data = response.json()
    return {
        "source": "Countries.dev",
        "raw": {
            "name": data.get("name"),
            "capital": data.get("capital"),
            "currency": data.get("currency")
        }
    }

async def fetch_ip(client: httpx.AsyncClient):
    """IP-API IP 기반 지역 정보 수집"""
    url = "http://ip-api.com/json/8.8.8.8"
    response = await client.get(url, timeout=10.0)
    response.raise_for_status()
    data = response.json()
    return {
        "source": "IP-API",
        "raw": {
            "ip": data.get("query"),
            "country": data.get("country"),
            "city": data.get("city")
        }
    }


# ===================================================================
# 3) 메인 파이프라인 (비동기 수집 -> Pydantic 검증 -> 저장 및 성능 비교)
# ===================================================================

async def main_pipeline():
    print("🚀 [1단계] asyncio + httpx로 3개 API 동시 수집 시작...")
    start_time = time.time()

    # asyncio.gather()를 사용하여 3개의 API 요청을 병렬(동시) 처리
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_weather(client),
            fetch_country(client),
            fetch_ip(client),
            return_exceptions=True
        )

    print(f"⏱️ API 동시 수집 소요 시간: {time.time() - start_time:.4f}초\n")

    # 🔍 [2단계] Pydantic v2 스키마 타입 및 범위 검증 수행
    print("🔍 [2단계] Pydantic v2 스키마 검증 시작...")
    validated_data = []

    for res in results:
        if isinstance(res, Exception) or res is None:
            continue

        source = res["source"]
        raw_data = res["raw"]

        try:
            # 출처에 맞는 Pydantic 모델에 데이터를 언패킹하여 검증
            if source == "Open-Meteo":
                record = WeatherRecord(**raw_data)
            elif source == "Countries.dev":
                record = CountryRecord(**raw_data)
            elif source == "IP-API":
                record = IPRecord(**raw_data)
            else:
                continue

            # 검증 통과 시 model_dump()로 딕셔너리 추출 후 리스트에 추가
            validated_data.append({"source": source, **record.model_dump()})
            print(f"  ✅ [{source}] 스키마 검증 통과! 데이터: {record.model_dump()}")
        except ValidationError as e:
            print(f"  ❌ [{source}] 스키마 검증 실패:\n{e}")

    if not validated_data:
        print("⚠️ 검증된 데이터가 없습니다.")
        return

    # Pandas DataFrame 변환
    df = pd.DataFrame(validated_data)

    # 💾 [3단계] CSV 및 Parquet 저장 포맷별 읽기/쓰기 성능 비교
    print("\n💾 [3단계] CSV vs Parquet 저장 및 읽기/쓰기 성능 비교 중...")
    
    csv_path = "output_data.csv"
    parquet_path = "output_data.parquet"

    # 1) CSV 형식 성능 측정 (쓰기 / 읽기)
    t0 = time.time()
    df.to_csv(csv_path, index=False, encoding="utf-8")
    csv_w = time.time() - t0

    t0 = time.time()
    pd.read_csv(csv_path, encoding="utf-8")
    csv_r = time.time() - t0

    # 2) Parquet 형식 성능 측정 (쓰기 / 읽기 - pyarrow 엔진 활용)
    try:
        t0 = time.time()
        df.to_parquet(parquet_path, index=False)
        par_w = time.time() - t0

        t0 = time.time()
        pd.read_parquet(parquet_path)
        par_r = time.time() - t0

        # 결과 리포트 출력
        print("\n" + "=" * 50)
        print("🏆 [성능 비교 리포트]")
        print("=" * 50)
        print(f"📁 [CSV]    - 쓰기: {csv_w:.6f}초 / 읽기: {csv_r:.6f}초")
        print(f"📦 [Parquet] - 쓰기: {par_w:.6f}초 / 읽기: {par_r:.6f}초")
        print("=" * 50)
    except Exception as e:
        print(f"⚠️ Parquet 저장 실패 (pyarrow 설치 확인 필요): {e}")


# ===================================================================
# 4) Pytest 단위 테스트 함수 정의 (pytest 실행 시 자동 인식)
# ===================================================================

def test_weather_record_success():
    """날씨 데이터 정상 범위 입력 테스트"""
    record = WeatherRecord(latitude=37.56, longitude=126.97, timezone="Asia/Seoul", hourly_temperatures_count=72)
    assert record.hourly_temperatures_count == 72

def test_weather_record_failure():
    """날씨 데이터 범위 위반(0 이하) 시 ValidationError 발생 테스트"""
    import pytest
    with pytest.raises(ValidationError):
        WeatherRecord(latitude=37.56, longitude=126.97, timezone="Asia/Seoul", hourly_temperatures_count=0)

def test_country_record_optional_currency():
    """국가 데이터에서 currency 필드가 None(Optional)일 때 허용되는지 테스트"""
    record = CountryRecord(name="Korea", capital="Seoul", currency=None)
    assert record.currency is None


if __name__ == "__main__":
    # 비동기 이벤트 루프를 통해 메인 파이프라인 실행
    asyncio.run(main_pipeline())