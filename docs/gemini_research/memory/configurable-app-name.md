# Configurable Android App Name Plan

## Objective
Enhance Android payload stealth by allowing users to customize the installed application's title via a new `APP_NAME` configurable variable, defaulting to stealthy system-like names.

## Scope & Impact
- Modify `source/core/android_kivy_generator.py` to retrieve `APP_NAME` from the configuration database.
- Use `APP_NAME` in the generation of the `buildozer.spec` file (`title` attribute).
- Update help documentation (`vars`) to reflect the new variable.

## Proposed Solution
1. **Retrieve Variable**: In `BuildozerPayloadGenerator.__init__`, fetch `APP_NAME` from the database.
2. **Set Defaults**: If `APP_NAME` is not explicitly set, determine the default based on the `ANDROID_PAYLOAD_TYPE`. 
   - `rootkit`: Default to "Google Play Services Core".
   - `drs` / `beacon`: Default to "Flappy Birds" (legacy default, or could change to something stealthier if desired, but sticking to existing logic for now unless instructed otherwise. Let's make the default for all unspecified be stealthy).
   - Let's update the fallback logic: If not set, use "Google Play Services".
3. **Apply to Spec**: The `self.app_name` variable is already used in `_write_buildozer_spec()`. Ensure it accurately reflects the user's choice or the stealthy default.
4. **Documentation**: Update `.data/.help/vars` and `.data/.help/android`.

## Implementation Steps
1. Use `replace` on `source/core/android_kivy_generator.py` to update the `__init__` method.
2. Use `replace` on `.data/.help/vars` to document `APP_NAME`.
3. Use `replace` on `.data/.help/android` to document the new stealth feature.
4. Log the change in `CHANGELOG.md`.

## Verification
Generating an APK without setting `APP_NAME` should result in an app named "Google Play Services". Setting `APP_NAME` to "My App" should result in an app named "My App".