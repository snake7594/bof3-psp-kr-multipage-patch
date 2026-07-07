BOF3 PSP 한국어 패치 v0.4.2-alpha

이 버전은 조합형 렌더링이 아닙니다.
완성형 한글 폰트 이미지를 ENDKANJI.EMI에 확장 배치하고,
대사 안의 한글을 대응 코드로 매핑해 출력하는 방식입니다.
FIRST.EMI와 BATL_RET.EMI의 기존 보조 폰트 페이지도 같은 방식으로 교체했습니다.
BOOT.BIN과 EBOOT.BIN을 모두 패치해 메뉴/대사 렌더러가 어느 실행 경로에서도 적용되게 했습니다.
v0.4의 시작 직후 크래시를 피하기 위해 FIRST.EMI와 BATL_RET.EMI는 원본 크기, 섹션 수, 기존 섹션 헤더 메타데이터를 유지합니다.

사용 방법

1. 이 폴더에 원본 ISO를 넣습니다.
2. 원본 ISO 파일 이름을 Breath of Fire III.iso 로 맞춥니다.
3. apply_iso_patch.bat 를 실행합니다.
4. BOF3_KR_fontimage_v0.4.2-alpha.iso 파일이 생성됩니다.

주의

- 이 패치는 PSP판 Breath of Fire III 원본 ISO용입니다.
- 원본 ISO MD5는 C7081C9C0865ECAEB6F4D2A42F865528 입니다.
- 생성 후 ISO MD5는 2CC49EC187146095ED4133035BACE782 입니다.
- 일본어 한자가 그대로 보이던 v0.3 문제를 줄이기 위해 BOOT.BIN과 보조 폰트 파일을 함께 패치했습니다.
- v0.4.1에서도 헤더 메타데이터가 바뀌어 시작 직후 크래시가 날 수 있어, 이번 버전은 해당 메타데이터도 원본 그대로 둡니다.
- 현재 버전은 alpha입니다. 추가 폰트 페이지의 실제 화면 출력은 PPSSPP/PSP에서 계속 확인이 필요합니다.
