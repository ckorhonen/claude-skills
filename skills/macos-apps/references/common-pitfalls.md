# Common Pitfalls in macOS App Development

Real failure modes from macOS development. These are the gotchas that prevent builds, cause app rejections, and lead to debugging nightmares.

## Sandboxing Violations

macOS sandboxing restricts what your app can access. Violating entitlements causes silent failures or App Store rejection.

### Entitlements Configuration Missing

**The error:** App compiles and runs locally, but crashes when sandboxed or rejected on App Store with "error: this app attempts to access private entitlements."

**Root cause:** You're accessing system resources (keychain, file system, network) without declaring them in `Entitlements.plist`.

**Fix:**
```bash
# 1. Open your project
open YourApp.xcodeproj

# 2. Go to Project → Build Settings → Code Signing Identity
# Ensure "Provisioning Profile" is set for your team

# 3. Add required entitlements
open YourApp/YourApp.entitlements
```

Common required entitlements:
```xml
<!-- Access keychain -->
<key>keychain-access-groups</key>
<array>
    <string>$(AppIdentifierPrefix)com.yourcompany.yourapp</string>
</array>

<!-- File access -->
<key>com.apple.security.files.user-selected.read-write</key>
<true/>

<!-- Network (always required if using URLSession) -->
<key>com.apple.security.network.client</key>
<true/>

<!-- Camera/Microphone (if used) -->
<key>com.apple.security.device.camera</key>
<true/>
<key>com.apple.security.device.microphone</key>
<true/>
```

### App Group Not Configured (for Extensions or Multi-App Communication)

**The error:** Extension crashes with `NSCocoaErrorDomain error 4099` or "the container is uninitialized." Host app and extension can't share data.

**Root cause:** App Group entitlement is declared but not configured in both the host app and extension, or the identifiers don't match.

**Fix:**
```bash
# In Xcode, for BOTH your app AND any extensions:
# 1. Target → Signing & Capabilities
# 2. + Capability → App Groups
# 3. Enter group identifier: group.com.yourcompany.yourapp

# Verify both have identical App Group identifiers
```

**Then use in code:**
```swift
// Both app and extension MUST use identical group identifier
let sharedDefaults = UserDefaults(suiteName: "group.com.yourcompany.yourapp")
```

If the identifiers don't match exactly, `UserDefaults(suiteName:)` silently fails and returns nil.

## Code Signing Failures

Code signing errors block shipping. These are often cryptic and can be solved by understanding what Xcode is checking.

### "No Provisioning Profile Found" or "Provisioning Profile is Invalid"

**The error:**
```
Error: "YourApp" requires a provisioning profile. Select a provisioning profile for the "Release" build configuration.
No provisioning profiles matching 'com.yourcompany.yourapp' were found.
```

**Root cause:** 
- Your bundle identifier doesn't match the provisioning profile
- Provisioning profile is expired (they last 1 year)
- Certificate was revoked or deleted from Apple Developer account

**Fix:**
```bash
# 1. Check your bundle identifier in Xcode
open YourApp.xcodeproj
# Project → Build Settings → Product Bundle Identifier

# 2. Go to Apple Developer (https://developer.apple.com)
# Account → Certificates, Identifiers & Profiles → Identifiers
# Verify your App ID matches your bundle identifier

# 3. Download fresh provisioning profile
# Certificates, Identifiers & Profiles → Profiles → Download
# Drag into Xcode → Organizer

# 4. In Xcode, set explicit provisioning profile
# Target → Build Settings → Provisioning Profile
# Select the freshly downloaded profile
```

### "Certificate not found in keychain"

**The error:**
```
error: Unable to locate an identity satisfying these requirements:
  - An Apple Distribution certificate
  - And a provisioning profile named 'Your App Distribution'

The bundle identifier of the application is invalid, its entitlements are invalid, or it was already distributed.
```

**Root cause:** Your code signing certificate (.p12 or .cer) isn't installed in the macOS keychain.

**Fix:**
```bash
# 1. Export your certificate from Apple Developer
# https://developer.apple.com → Certificates, Identifiers & Profiles
# Certificate → Download (gets .cer file)

# 2. Double-click the .cer file to import to Keychain
# OR import via command line:
security import certificate.cer -k ~/Library/Keychains/login.keychain

# 3. Verify it's in Keychain
security find-identity -v -p codesigning ~/Library/Keychains/login.keychain

# 4. In Xcode, rebuild
# Build → Clean Build Folder (Cmd+Shift+K)
# Then build again
```

### "Provisioning Profile Doesn't Include Entitlements"

**The error:**
```
error: Provisioning profile 'Your App' doesn't include the com.apple.security.application-groups entitlement required for target 'YourApp'.
```

**Root cause:** You added an entitlement in Xcode, but your provisioning profile wasn't regenerated to include it. Apple's servers don't automatically update profiles.

**Fix:**
```bash
# 1. In Xcode, note which entitlements you added (usually in red highlighting)

# 2. Go to Apple Developer → Certificates, Identifiers & Profiles
#    → Identifiers → Your App ID
#    → Edit → Confirm the entitlements are listed
#    → If not, add them

# 3. Delete and re-download the provisioning profile
#    → Profiles → Select your profile → Delete
#    → Create new profile for the same app
#    → Download

# 4. Drag the new .mobileprovision file into Xcode → Window → Organizer → Accounts
```

## App Store Rejection Patterns

These rejections are common and preventable.

### Private API Usage ("Uses private/undocumented APIs")

**The rejection:**
```
Your app uses private APIs, which are not permitted on the App Store. 
Specifically, we found references to:
  - ClassPrivateName
  - _privateMethod()
```

**Root cause:** You called a private API (prefixed with `_` or not in public documentation). Apple scans binaries for these.

**Common private API mistakes:**
```swift
// ❌ WRONG - Private API
import AppKit

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        // This function isn't available on all macOS versions - private usage
        return true
    }
}

// ❌ WRONG - Using private method
let nsApplication = NSApplication.shared
nsApplication.requestUserAttention(NSApplication.RequestUserAttentionType.criticalRequest)
// Might not exist in all versions

// ✅ CORRECT - Check availability
if #available(macOS 10.15, *) {
    // Only use public APIs with availability checks
}
```

**Fix:**
```bash
# 1. Search codebase for underscore-prefixed calls
grep -r "_[a-zA-Z]" YourApp/
# Review results - anything starting with _ is likely private

# 2. Check against public documentation
# Apple Reference → macOS → Your framework name

# 3. Use availability guards for uncertain APIs
@available(macOS 10.15, *)
func doSomething() {
    // Safe - only compiled for macOS 10.15+
}
```

### Missing or Incorrect Metadata (App Name, Version, Privacy Policy)

**The rejection:**
```
Missing required fields:
  - App Version Number missing
  - Category missing
  - Your app references health/medical functionality but doesn't have privacy policy
```

**Root cause:** Info.plist is incomplete or version doesn't match.

**Fix:**
```bash
# 1. In Xcode, verify Info.plist is configured
open YourApp/Info.plist

# Required fields:
# - CFBundleVersion (e.g., "1")
# - CFBundleShortVersionString (e.g., "1.0.0")
# - CFBundleName (app name, max 30 chars)
# - NSHumanReadableCopyright (copyright notice)

# 2. If using privacy policy, ensure it's reachable
# https://yoursite.com/privacy

# 3. In Xcode, verify:
# Target → General → Version / Build numbers match CFBundle values
```

## SwiftUI State Management Bugs

These cause views that don't update or unexpected state behavior.

### @Bindable Not Used with SwiftData @Model

**The bug:** Child view receives a @Model object but uses `let` instead of `@Bindable`. Changes to the model don't update the view.

```swift
// ❌ WRONG - Model changes not observed
struct CardEditView: View {
    let card: Card  // @Model object, but not using @Bindable

    var body: some View {
        TextField("Title", text: $card.title)  // ERROR: Can't create binding
    }
}

// ✅ CORRECT
struct CardEditView: View {
    @Bindable var card: Card  // Proper observation

    var body: some View {
        TextField("Title", text: $card.title)  // Works
    }
}
```

**The error you'll see:**
```
Cannot convert value of type 'Binding<String>' to expected argument type 'Binding<String>'
```

**Fix:**
```swift
// Always use @Bindable when:
// 1. Passing @Model objects to child views
// 2. Creating bindings to model properties
// 3. The child view should react to model changes

@Bindable var model: YourModel
```

### View Updates Stopped After State Change

**The bug:** You change a @State variable, but the view doesn't rebuild. Usually happens when:
- State is wrapped in a class that's mutable but not @Observable
- You modify a struct in-place instead of replacing it

```swift
// ❌ WRONG - Modifying mutable class directly
@State private var viewModel = DataViewModel()  // Class, not @Observable

var body: some View {
    Button("Update") {
        viewModel.data.append("new")  // Direct mutation, no view update
    }
}

// ✅ CORRECT - Use @Observable or @State with value types
@State private var data: [String] = []

var body: some View {
    Button("Update") {
        data.append("new")  // Struct mutation triggers update
    }
}

// OR use @Observable for classes
@Observable
class DataViewModel {
    var data: [String] = []
}

@State private var viewModel = DataViewModel()
```

**Fix:**
```swift
// For mutable view model classes, use @Observable
import Observation

@Observable
class MyViewModel {
    var state: String = ""
    
    func updateState() {
        self.state = "updated"  // This WILL notify SwiftUI
    }
}

struct MyView: View {
    @State private var viewModel = MyViewModel()
    
    var body: some View {
        Text(viewModel.state)  // Updates when state changes
    }
}
```

### NavigationStack Doesn't Update

**The bug:** `NavigationStack` with @State-managed navigation path doesn't navigate when you update the state.

```swift
// ❌ WRONG - Path doesn't trigger navigation
@State private var navigationPath: NavigationPath = NavigationPath()

var body: some View {
    NavigationStack(path: $navigationPath) {
        List(items) { item in
            NavigationLink(value: item) {
                Text(item.name)
            }
        }
    }
}

func goToItem(_ item: Item) {
    navigationPath.append(item)  // Doesn't work reliably
}

// ✅ CORRECT - Use explicit @State tracking
@State private var selectedItem: Item? = nil

var body: some View {
    NavigationStack(path: $navigationPath) {
        List(items) { item in
            NavigationLink(value: item) {
                Text(item.name)
            }
        }
    }
}
```

## macOS Version Compatibility

Calling unavailable APIs crashes on older macOS versions.

### Using API That Doesn't Exist on Target macOS

**The crash:** App launches fine on macOS 14, but crashes on macOS 12:
```
Terminating app due to uncaught exception 'NSInvalidArgumentException', 
reason: 'unrecognized selector sent to instance'
```

**Root cause:** You used an API introduced in macOS 14, but your deployment target is macOS 12.

**Fix:**
```swift
// 1. Always use availability guards
if #available(macOS 13.0, *) {
    // New API from macOS 13+
    someNewFeature()
} else {
    // Fallback for older versions
    someOldWayOfDoingIt()
}

// 2. Check target macOS in Xcode
// Project → Build Settings → Minimum Deployment Target (macOS)
// Should match your minimum supported version

// 3. Xcode will warn you if you use unavailable APIs
@available(macOS 13.0, *)
func newFunction() {
    // This function only exists on macOS 13+
}
```

### Deprecated API Still Used

**The warning:** Xcode shows deprecation warnings, you ignore them, users on new macOS get worse performance or behavior.

```swift
// ❌ WRONG - Deprecated, noisy warnings
NSFont.systemFont(ofSize: 12)  // Deprecated since macOS 10.15

// ✅ CORRECT - Use new API
Font.system(size: 12)
```

**Fix:**
```bash
# 1. In Xcode, build and note all deprecation warnings
# 2. For each one, use the suggested replacement (Xcode will hint)
# 3. Test on both old and new macOS versions

# Common replacements:
# - NSFont → Font (SwiftUI)
# - NSView layouts → Auto Layout or VStack/HStack
# - AppKit extensions → Native SwiftUI equivalents
```

---

## Debugging Xcode Errors

### "Undefined symbol" with Linker Error

**The error:**
```
Undefined symbol: _$s9YourAppC18someVariableCodeS3StringVvp
```

**Root cause:** Usually a missing file in Build Phases → Compile Sources, or a broken bridging header.

**Fix:**
```bash
# 1. Clean build
xcodebuild clean build

# 2. Check all files are in Compile Sources
# Target → Build Phases → Compile Sources
# If file is missing, drag it in

# 3. If using Objective-C bridge, verify it exists
# Check: YourApp-Bridging-Header.h
# Verify it's set in Build Settings → Bridging Header

# 4. Rebuild
xcodebuild build
```

### "Module not found" When Importing Swift Package

**The error:**
```
error: could not find or load required modules for target 'YourApp'
```

**Root cause:** Package is listed in dependencies but not added to the target.

**Fix:**
```bash
# 1. In Xcode, Target → Build Phases → Link Binary with Libraries
# Verify the framework is listed

# 2. If not, add it:
# + → Select the framework
# OK

# 3. Rebuild
xcodebuild build
```

---

## Performance Pitfalls

### Main Thread Blocking with Heavy Work

**The symptom:** App freezes for 1-2 seconds when doing network requests or file I/O.

**Root cause:** You're doing blocking work on the main thread instead of using `async/await`.

**Fix:**
```swift
// ❌ WRONG - Blocks main thread
@State private var data: [Item] = []

func loadData() {
    let url = URL(string: "https://api.example.com/items")!
    let (data, _) = try! URLSession.shared.data(from: url)  // BLOCKING!
    let decoded = try! JSONDecoder().decode([Item].self, from: data)
    self.data = decoded  // Updates UI after freeze
}

// ✅ CORRECT - Async work
func loadData() async {
    let url = URL(string: "https://api.example.com/items")!
    let (data, _) = try await URLSession.shared.data(from: url)  // Non-blocking
    let decoded = try JSONDecoder().decode([Item].self, from: data)
    self.data = decoded  // Updates smoothly
}
```

This section should be referenced in the main SKILL.md file.
