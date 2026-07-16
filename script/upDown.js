function randomNum() {

    // 1. 게임이 시작될 때마다 새롭게 무작위 비밀 숫자를 고릅니다.
    var computerNum = Math.floor(Math.random() * 50) + 1;
    var count = 0;

    // 치트키 콘솔로그 (F12 콘솔 탭에서 확인 가능)
    console.log(computerNum);

    // 2. 본격적인 게임 무한 루프 시작
    while (true) {
        var userGuess = Number(prompt("1부터 50 사이의 숫자 중 컴퓨터가 생각한 숫자는 무엇일까요?"));
        
        // 사용자가 취소 버튼을 누르거나 창을 닫으면 게임을 즉시 종료하는 예외 처리 방어코드
        if (userGuess === 0) {
            alert("게임이 취소되었습니다.");
            break;
        }

        count = count + 1;

        if (userGuess === computerNum) {
            alert("🎉 정답입니다! 축하합니다!\n👉 도전 횟수: " + count + "번 만에 맞추셨습니다.");
            break; 
            
        } else if (userGuess > computerNum) {
            alert("🔽 Down! 더 작은 숫자를 입력해 보세요. (현재 " + count + "회 도전 중)");
            
        } else if (userGuess < computerNum) {
            alert("🔼 Up! 더 큰 숫자를 입력해 보세요. (현재 " + count + "회 도전 중)");
            
        } else {
            alert("⚠️ 올바른 숫자를 입력하지 않으셨습니다. 다시 시도해 주세요.");
        }
    }
}