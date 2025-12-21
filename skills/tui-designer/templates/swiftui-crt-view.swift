/**
 * SwiftUI CRT Terminal View Template
 *
 * A complete SwiftUI view demonstrating CRT effects using Metal shaders.
 * Includes neon glow, scanlines, and retro terminal styling.
 *
 * Requirements:
 *   - iOS 17+ / macOS Sonoma+
 *   - Add CRT.metal to your Xcode project
 */

import SwiftUI

// MARK: - Color Extensions

extension Color {
    // Phosphor Green Palette
    static let phosphorBright = Color(red: 0, green: 1, blue: 0)
    static let phosphorMedium = Color(red: 0, green: 0.8, blue: 0)
    static let phosphorDim = Color(red: 0, green: 0.6, blue: 0)
    static let phosphorBg = Color(red: 0, green: 0.067, blue: 0)
    static let phosphorBgDeep = Color(red: 0, green: 0.031, blue: 0)

    // Cyberpunk Palette
    static let cyberCyan = Color(red: 0, green: 1, blue: 1)
    static let cyberMagenta = Color(red: 1, green: 0, blue: 1)
    static let cyberPink = Color(red: 1, green: 0.078, blue: 0.576)
    static let cyberBg = Color(red: 0.039, green: 0.039, blue: 0.102)

    // Amber Palette
    static let amberBright = Color(red: 1, green: 0.69, blue: 0)
    static let amberDim = Color(red: 0.6, green: 0.41, blue: 0)
    static let amberBg = Color(red: 0.102, green: 0.063, blue: 0)
}

// MARK: - CRT Effect Modifier

struct CRTEffectModifier: ViewModifier {
    @State private var startTime = Date()

    var scanlineIntensity: Float
    var distortionStrength: Float
    var chromaticStrength: Float
    var flickerIntensity: Float

    init(
        scanlineIntensity: Float = 0.1,
        distortionStrength: Float = 0.08,
        chromaticStrength: Float = 0.003,
        flickerIntensity: Float = 0.02
    ) {
        self.scanlineIntensity = scanlineIntensity
        self.distortionStrength = distortionStrength
        self.chromaticStrength = chromaticStrength
        self.flickerIntensity = flickerIntensity
    }

    func body(content: Content) -> some View {
        TimelineView(.animation) { timeline in
            let elapsedTime = Float(timeline.date.timeIntervalSince(startTime))

            GeometryReader { geometry in
                content
                    .layerEffect(
                        ShaderLibrary.crtEffect(
                            .float(elapsedTime),
                            .float2(geometry.size),
                            .float(scanlineIntensity),
                            .float(distortionStrength),
                            .float(chromaticStrength),
                            .float(flickerIntensity)
                        ),
                        maxSampleOffset: CGSize(width: 10, height: 10)
                    )
            }
        }
    }
}

extension View {
    func crtEffect(
        scanlines: Float = 0.1,
        distortion: Float = 0.08,
        chromatic: Float = 0.003,
        flicker: Float = 0.02
    ) -> some View {
        modifier(CRTEffectModifier(
            scanlineIntensity: scanlines,
            distortionStrength: distortion,
            chromaticStrength: chromatic,
            flickerIntensity: flicker
        ))
    }
}

// MARK: - Neon Glow Modifier

extension View {
    func neonGlow(color: Color, radius: CGFloat = 10) -> some View {
        self
            .shadow(color: color.opacity(0.9), radius: radius * 0.25, x: 0, y: 0)
            .shadow(color: color.opacity(0.7), radius: radius * 0.5, x: 0, y: 0)
            .shadow(color: color.opacity(0.5), radius: radius, x: 0, y: 0)
            .shadow(color: color.opacity(0.3), radius: radius * 2, x: 0, y: 0)
    }

    func neonGlowIntense(color: Color) -> some View {
        self
            .shadow(color: .white.opacity(0.9), radius: 2, x: 0, y: 0)
            .shadow(color: color.opacity(0.9), radius: 5, x: 0, y: 0)
            .shadow(color: color.opacity(0.7), radius: 10, x: 0, y: 0)
            .shadow(color: color.opacity(0.5), radius: 20, x: 0, y: 0)
            .shadow(color: color.opacity(0.3), radius: 40, x: 0, y: 0)
    }
}

// MARK: - Pulsing Neon Modifier

struct NeonPulseModifier: ViewModifier {
    @State private var intensity: CGFloat = 1.0
    let color: Color
    let duration: Double

    func body(content: Content) -> some View {
        content
            .shadow(color: color.opacity(0.9 * intensity), radius: 5, x: 0, y: 0)
            .shadow(color: color.opacity(0.6 * intensity), radius: 15, x: 0, y: 0)
            .shadow(color: color.opacity(0.3 * intensity), radius: 30, x: 0, y: 0)
            .onAppear {
                withAnimation(.easeInOut(duration: duration).repeatForever(autoreverses: true)) {
                    intensity = 0.6
                }
            }
    }
}

extension View {
    func neonPulse(color: Color, duration: Double = 1.5) -> some View {
        modifier(NeonPulseModifier(color: color, duration: duration))
    }
}

// MARK: - Terminal Text Style

extension Text {
    func terminalStyle(size: CGFloat = 14) -> some View {
        self
            .font(.system(size: size, design: .monospaced))
            .tracking(0)
    }

    func terminalHeader() -> some View {
        self
            .font(.system(size: 16, weight: .bold, design: .monospaced))
            .textCase(.uppercase)
            .tracking(2)
    }
}

// MARK: - Blinking Cursor

struct BlinkingCursor: View {
    @State private var visible = true

    var body: some View {
        Text("_")
            .font(.system(size: 14, design: .monospaced))
            .opacity(visible ? 1 : 0)
            .onAppear {
                Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
                    visible.toggle()
                }
            }
    }
}

// MARK: - Terminal Line

struct TerminalLine: View {
    let prefix: String
    let content: String
    let color: Color

    init(_ content: String, prefix: String = ">", color: Color = .phosphorBright) {
        self.prefix = prefix
        self.content = content
        self.color = color
    }

    var body: some View {
        HStack(spacing: 4) {
            Text(prefix)
                .foregroundColor(color.opacity(0.6))
            Text(content)
                .foregroundColor(color)
        }
        .font(.system(size: 14, design: .monospaced))
    }
}

// MARK: - Progress Bar (ASCII Style)

struct ASCIIProgressBar: View {
    let value: Double // 0.0 - 1.0
    let width: Int
    let color: Color

    init(value: Double, width: Int = 20, color: Color = .phosphorBright) {
        self.value = min(1, max(0, value))
        self.width = width
        self.color = color
    }

    var body: some View {
        let filled = Int(Double(width) * value)
        let empty = width - filled

        Text("[" + String(repeating: "=", count: filled) + String(repeating: " ", count: empty) + "]")
            .font(.system(size: 14, design: .monospaced))
            .foregroundColor(color)
    }
}

// MARK: - Status Badge

struct StatusBadge: View {
    enum Status {
        case online, offline, warning, error
    }

    let status: Status
    let label: String

    var statusIcon: String {
        switch status {
        case .online: return "●"
        case .offline: return "○"
        case .warning: return "◐"
        case .error: return "◉"
        }
    }

    var statusColor: Color {
        switch status {
        case .online: return .phosphorBright
        case .offline: return .gray
        case .warning: return .yellow
        case .error: return .red
        }
    }

    var body: some View {
        HStack(spacing: 4) {
            Text(statusIcon)
                .foregroundColor(statusColor)
            Text(label)
                .foregroundColor(.phosphorMedium)
        }
        .font(.system(size: 12, design: .monospaced))
    }
}

// MARK: - Terminal Card

struct TerminalCard<Content: View>: View {
    let title: String
    let color: Color
    @ViewBuilder let content: () -> Content

    init(title: String, color: Color = .phosphorBright, @ViewBuilder content: @escaping () -> Content) {
        self.title = title
        self.color = color
        self.content = content
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Header
            HStack {
                Text("┌─ \(title) ")
                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                    .textCase(.uppercase)
                Text(String(repeating: "─", count: 20))
                    .font(.system(size: 14, design: .monospaced))
                Text("┐")
                    .font(.system(size: 14, design: .monospaced))
            }
            .foregroundColor(color)

            // Content
            HStack {
                Text("│")
                    .font(.system(size: 14, design: .monospaced))
                    .foregroundColor(color.opacity(0.5))

                VStack(alignment: .leading, spacing: 4) {
                    content()
                }
                .padding(.horizontal, 8)

                Spacer()

                Text("│")
                    .font(.system(size: 14, design: .monospaced))
                    .foregroundColor(color.opacity(0.5))
            }

            // Footer
            HStack {
                Text("└")
                    .font(.system(size: 14, design: .monospaced))
                Text(String(repeating: "─", count: 30))
                    .font(.system(size: 14, design: .monospaced))
                Text("┘")
                    .font(.system(size: 14, design: .monospaced))
            }
            .foregroundColor(color)
        }
        .padding(8)
    }
}

// MARK: - Main Terminal View

struct RetroTerminalView: View {
    @State private var bootComplete = false
    @State private var lines: [String] = []
    @State private var cpuUsage: Double = 0.45
    @State private var memoryUsage: Double = 0.62

    let bootMessages = [
        "INITIALIZING SYSTEM...",
        "LOADING CORE MODULES...",
        "ESTABLISHING SECURE CONNECTION...",
        "AUTHENTICATING USER...",
        "SYSTEM READY"
    ]

    var body: some View {
        ZStack {
            // Background
            Color.phosphorBgDeep
                .ignoresSafeArea()

            // Content
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Header
                    Text("SYSTEM MONITOR v2.1")
                        .terminalHeader()
                        .foregroundColor(.phosphorBright)
                        .neonGlow(color: .phosphorMedium, radius: 8)

                    Divider()
                        .background(Color.phosphorDim)

                    if bootComplete {
                        // Status Cards
                        HStack(spacing: 16) {
                            TerminalCard(title: "CPU") {
                                Text("\(Int(cpuUsage * 100))%")
                                    .terminalStyle(size: 24)
                                    .foregroundColor(.phosphorBright)
                                ASCIIProgressBar(value: cpuUsage, width: 15)
                            }

                            TerminalCard(title: "Memory") {
                                Text("\(Int(memoryUsage * 100))%")
                                    .terminalStyle(size: 24)
                                    .foregroundColor(.phosphorBright)
                                ASCIIProgressBar(value: memoryUsage, width: 15)
                            }
                        }

                        // Status
                        TerminalCard(title: "Services") {
                            StatusBadge(status: .online, label: "nginx")
                            StatusBadge(status: .online, label: "postgres")
                            StatusBadge(status: .warning, label: "redis")
                            StatusBadge(status: .offline, label: "worker-2")
                        }

                        // Log output
                        TerminalCard(title: "Output") {
                            ForEach(lines, id: \.self) { line in
                                TerminalLine(line)
                            }
                            HStack(spacing: 0) {
                                Text("> ")
                                    .foregroundColor(.phosphorDim)
                                BlinkingCursor()
                                    .foregroundColor(.phosphorBright)
                            }
                            .font(.system(size: 14, design: .monospaced))
                        }
                    } else {
                        // Boot sequence
                        ForEach(lines, id: \.self) { line in
                            TerminalLine(line, prefix: "[SYS]")
                        }
                    }
                }
                .padding()
            }
        }
        .crtEffect(
            scanlines: 0.12,
            distortion: 0.05,
            chromatic: 0.002,
            flicker: 0.01
        )
        .onAppear {
            runBootSequence()
        }
    }

    func runBootSequence() {
        for (index, message) in bootMessages.enumerated() {
            DispatchQueue.main.asyncAfter(deadline: .now() + Double(index) * 0.5) {
                withAnimation {
                    lines.append(message)
                }

                if index == bootMessages.count - 1 {
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                        withAnimation {
                            bootComplete = true
                            lines = ["System initialized successfully"]
                        }
                        startMetricsUpdates()
                    }
                }
            }
        }
    }

    func startMetricsUpdates() {
        Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
            withAnimation {
                cpuUsage = max(0.1, min(0.9, cpuUsage + Double.random(in: -0.1...0.1)))
                memoryUsage = max(0.3, min(0.95, memoryUsage + Double.random(in: -0.05...0.05)))
            }
        }
    }
}

// MARK: - Preview

#Preview {
    RetroTerminalView()
        .preferredColorScheme(.dark)
}
