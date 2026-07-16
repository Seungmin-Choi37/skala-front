function showMyBag() {
    // 1. [Object가 담긴 Array] 객체들이 담긴 배열 데이터
    var myBag = [
        { name: "여권 ✈️", count: 1 },
        { name: "스마트폰 📱", count: 2 },
        { name: "지갑 💳", count: 1 }
    ];

    // 2. 출력할 텍스트 기본 세팅
    var resultText = "🎒 [내 가방 속 물품 목록]\n-----------------------\n";

    // 3. ★ for...in 루프 활용
    // myBag 배열의 인덱스(0, 1, 2...)를 순서대로 변수 i에 자동으로 넣어줍니다.
    for (var i in myBag) {
        // i가 알아서 방 번호가 되므로 기존과 동일하게 접근 가능합니다.
        resultText = resultText + "- " + myBag[i].name + " : " + myBag[i].count + "개\n";
    }

    resultText = resultText + "-----------------------\n";
    resultText = resultText + "총 물품 종류: " + myBag.length + "가지";

    // 4. 알림창 출력
    alert(resultText);
}