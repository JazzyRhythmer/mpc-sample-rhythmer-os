# Rhythmer OS 0.2.0

Developed by jazzy rhythmer. This is a beta package for owner-led MPC Sample testing. Hardware validation is pending; it is not labelled as completed. No device installation or public upload is performed by the packaging tools.


Before handing off a beta, the build runs unit/sanitizer checks, host playback and independent-instance/project-state checks, original generator seed/role/range checks, shell Undo/Redo, self-test audio, monkey input and UI/boot renders. Packaging requires unchanged accepted native-plugin hashes and a stamped tested runtime. Source archives, required notices, file checksums and privacy checks accompany the SD archive. See VERIFICATION.md for the observed results and ENGINE_REGISTRY.md for exclusions.

## Owner beta test

1. Retain the existing SD contents and a working stock/recovery path. Check the firmware compatibility stated in SD_CARD_GUIDE.md before copying the beta.
2. Check startup, skip/transition, display contrast, controls and return to the stock MPC app.
3. Audition the instruments and all intended kits at useful velocity levels; check levels, long releases, hat choke, panic/stop and simultaneous track playback.
4. Test SEQ Generate/Mutate and Break using owned audio. Save, restart and reload projects with the chosen instruments.
5. Measure the intended project's CPU, timing, audio stability and latency on the device. Record the actual device/firmware, beta version and results before publishing.

The package carries no global 32-voice cap. Each original engine retains its allocation policy. Heavy instruments allocate their original resources when selected; installed source folders do not imply simultaneous active engines. Open MPC's existing wrapper mutex and external-module loading behaviour remain real-device performance considerations. This is not a hard-real-time certification.

Mandatory origin credit: Based on Melodee by Kerem Kiliç (Ellic Studio), AGPL-3.0-only, and sample-base. Original engine copyright, license and compatibility identities remain intact.

GEN의 트랙 범위·악기 자동 배정·MIDI 전용 모드와 1–4마디 Break 자동 준비는 [GEN_WORKFLOW.md](GEN_WORKFLOW.md)를 참고하세요.

For this structural update also test patterns A-H, Freeze/Deep Freeze and thaw with Rhythmer Kit, GEN frozen-track prompts, USB web/file access and screen mirror, plus signed update and restart rollback on the actual device. See UPSTREAM_030.md.
