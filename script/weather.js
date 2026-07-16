const citySelect = document.querySelector('#city-select');
const weatherBox = document.querySelector('#weather-box');

// ★ 이벤트 핸들러 함수 앞에 async를 붙여줍니다!
citySelect.addEventListener('change', async function(event) {
    const selectedValue = event.target.value;
    
    if (selectedValue === "none") {
        weatherBox.innerHTML = "<p>도시를 선택하면 좌표가 표시됩니다.</p>";
        return;
    }

    const coords = selectedValue.split(',');
    const lat = coords[0];
    const lon = coords[1];
    const cityName = citySelect.options[citySelect.selectedIndex].text;

    // [UX 개선] 서버에서 데이터를 가져오는 동안 로딩 표시 띄우기
    weatherBox.innerHTML = "<p>실시간 날씨 로딩 중... ⏳</p>";

    // try-catch 구문으로 네트워크 에러 방어벽 치기
    try {
        // Open-Meteo API에 비동기 요청 날리기
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m`;
        
        // await를 붙여서 데이터가 인터넷 너머에서 다 올 때까지 안전하게 기다림
        const response = await fetch(url);
        const data = await response.json();

        // API 내부의 실시간 온도와 습도 변수 쏙 빼오기
        const currentTemp = data.current.temperature_2m;
        const currentHumidity = data.current.relative_humidity_2m;

        // 최종 진짜 데이터를 DOM에 주입!
        weatherBox.innerHTML = `
            <div style="background-color: #f1f2f6; padding: 15px; border-radius: 6px; margin-top: 10px;">
                <h4>🌍 ${cityName} 실시간 날씨</h4>
                <p>🌡️ 현재 기온: <strong>${currentTemp}°C</strong></p>
                <p>💧 현재 습도: <strong>${currentHumidity}%</strong></p>
            </div>
        `;

    } catch (error) {
        weatherBox.innerHTML = "<p>⚠️ 날씨 정보를 가져오는데 실패했습니다.</p>";
        console.error(error);
    }
});