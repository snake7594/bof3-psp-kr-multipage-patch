# BOF3 한글패치 준비 기록

## 원본

- 깨끗한 ISO: `C:\Users\Jae Ho Lee\Pictures\psp\roms\BOF3\Breath of Fire III.iso`
- ISO 크기: `403,963,904` bytes
- ISO MD5: `C7081C9C0865ECAEB6F4D2A42F865528`
- 기존 분석 트리: `C:\Users\Jae Ho Lee\Pictures\psp\roms\Breath of Fire III`

## 작업 트리

- 패치 작업 트리: `work\bof3_patch_prep\patch_tree`
- ISO 추출 파일: 1,846개
- 복사한 자산: `_ko`, 폰트 자산, codec/injection/build 스크립트, 매핑 데이터

## 진행 순서

1. 깨끗한 ISO를 `pycdlib`로 추출했습니다.
2. 기존 한글패치 분석 트리에서 번역/도구/폰트 자산을 복사했습니다.
3. ISO에서 추출한 원본 `BOOT.BIN`, `EBOOT.BIN`, `ENDKANJI.EMI`를 `.orig`로 보존했습니다.
4. 기존 조합형 경로를 재현해 이전 분석 결과와 같은 패치 트리를 만들었습니다.
5. 조합형의 표시 문제를 피하기 위해 완성형 한글 경로를 새로 구성했습니다.
6. 441자 완성형 안정안을 만든 뒤, 추가 폰트 페이지 접근 실험으로 확장했습니다.

## 현재 결론

- 441자만으로는 모든 대사를 무손실 수용할 수 없습니다.
- 기호/가나 영역을 최대한 활용하면 약 656자까지 가능합니다.
- 추가 페이지 접근 실험을 통해 1,323칸을 확보했고, 현재 번역의 1,147자를 전부 수용했습니다.
- 현재 배포는 ISO용 xdelta 패치 방식입니다.
