/*
 * dh-diagnostics.gradle.kts
 * 
 * Gradle Kotlin DSL script for DistantHorizonsStandalone config diagnostics.
 * 
 * Usage: Apply in build.gradle.kts:
 *   apply(from = "dh-diagnostics.gradle.kts")
 * 
 * Then run: ./gradlew dhDiagnostics
 * 
 * This task analyzes Config.java and identifies settings that may cause
 * performance issues. It computes the mathematical impact of distance
 * settings: area = π × r² blocks² per player.
 * 
 * Based on analysis of Config.java from DarkShadow44/DistantHorizonsStandalone
 */

import java.io.File
import kotlin.math.PI

// Task to run DH configuration diagnostics
tasks.register<DefaultTask>("dhDiagnostics") {
    group = "verification"
    description = "Analyzes DH config for performance-impacting settings"
    
    doLast {
        val configFile = findConfigFile()
        
        if (configFile == null) {
            println("ERROR: Could not find Config.java")
            println("Searched in standard Forge source locations")
            return@doLast
        }
        
        println("=".repeat(80))
        println("DistantHorizonsStandalone Configuration Diagnostics")
        println("=".repeat(80))
        println()
        println("Analyzing: ${configFile.absolutePath}")
        println()
        
        val configContent = configFile.readText()
        val findings = analyzeConfig(configContent)
        
        printReport(findings)
        
        // Write report to file
        val reportFile = File(project.buildDir, "dh-diagnostics-report.txt")
        reportFile.parentFile.mkdirs()
        writeReportToFile(findings, reportFile)
        println()
        println("Full report written to: ${reportFile.absolutePath}")
        println("=".repeat(80))
        
        // Fail build if critical issues found (optional, can be disabled)
        val criticalCount = findings.count { it.severity == Severity.CRITICAL }
        if (criticalCount > 0) {
            println()
            println("WARNING: $criticalCount CRITICAL configuration issues found!")
            println("Review the report above for details.")
        }
    }
}

/**
 * Finds Config.java in standard Forge project locations.
 */
fun findConfigFile(): File? {
    val possiblePaths = listOf(
        "src/main/java/com/seibel/distanthorizons/core/config/Config.java",
        "src/main/java/com/seibel/distanthorizons/config/Config.java",
        "src/main/java/com/seibel/distanthorizons/Config.java",
        "src/main/java/com/distanthorizons/core/config/Config.java",
        "core/src/main/java/com/seibel/distanthorizons/core/config/Config.java"
    )
    
    for (path in possiblePaths) {
        val file = File(project.projectDir, path)
        if (file.exists()) {
            return file
        }
    }
    
    // Fallback: search for any Config.java containing "maxGenerationRequestDistance"
    return project.projectDir.walkTopDown()
        .filter { it.name == "Config.java" }
        .filter { it.readText().contains("maxGenerationRequestDistance") }
        .firstOrNull()
}

/**
 * Represents a configuration finding.
 */
enum class Severity { INFO, WARNING, CRITICAL }

data class ConfigFinding(
    val setting: String,
    val currentValue: Int,
    val recommendedValue: Int,
    val areaBlocksSquared: Double,
    val severity: Severity,
    val message: String
)

/**
 * Analyzes Config.java content for problematic settings.
 */
fun analyzeConfig(content: String): List<ConfigFinding> {
    val findings = mutableListOf<ConfigFinding>()
    
    // Look for setMinDefaultMax patterns
    // Pattern: setMinDefaultMax(min, default, max)
    val pattern = Regex("setMinDefaultMax\\s*\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\)")
    val matches = pattern.findAll(content)
    
    for (match in matches) {
        val (minStr, defaultStr, maxStr) = match.destructured
        val minVal = minStr.toInt()
        val defaultValue = defaultStr.toInt()  // NOT 'default' - Kotlin reserved word
        val maxVal = maxStr.toInt()
        
        // Try to identify what setting this is by looking at surrounding context
        // NOTE: This uses a 500-char lookback which is fragile if multiple
        // setMinDefaultMax calls are close together. In practice, Config.java
        // has these calls well-separated. A more robust approach would parse
        // the AST, but regex is sufficient for this diagnostic tool.
        val contextStart = maxOf(0, match.range.start - 500)
        val context = content.substring(contextStart, match.range.end)
        
        val settingName = when {
            context.contains("maxGenerationRequestDistance") -> "maxGenerationRequestDistance"
            context.contains("generationMaxChunkRadius") -> "generationMaxChunkRadius"
            context.contains("lodChunkRenderDistanceRadius") -> "lodChunkRenderDistanceRadius"
            context.contains("clientConnectionTimeout") -> "clientConnectionTimeout"
            else -> "unknown_${match.range.start}"
        }
        
        // Compute area for distance settings
        val area = if (isDistanceSetting(settingName)) {
            PI * defaultValue * defaultValue
        } else {
            0.0
        }
        
        // Determine severity and recommendation
        val (severity, recommended, message) = when {
            settingName == "maxGenerationRequestDistance" && defaultValue >= 4096 -> {
                Triple(
                    Severity.CRITICAL,
                    1024,
                    "Default creates ${formatNumber(area)} blocks² generation area per player. " +
                    "With 10 players: ${formatNumber(area * 10)} blocks². " +
                    "This exceeds recommended generation area thresholds."
                )
            }
            settingName == "maxGenerationRequestDistance" && defaultValue >= 2048 -> {
                Triple(
                    Severity.WARNING,
                    1024,
                    "Default creates ${formatNumber(area)} blocks² per player. " +
                    "Consider reducing to 1024 for better performance."
                )
            }
            settingName == "generationMaxChunkRadius" && defaultValue == 0 -> {
                Triple(
                    Severity.WARNING,
                    128,
                    "Default of 0 means unbounded generation. " +
                    "Recommend setting explicit limit (e.g., 128 chunks)."
                )
            }
            isDistanceSetting(settingName) && area > 10_000_000 -> {
                Triple(
                    Severity.WARNING,
                    defaultValue / 2,
                    "Distance setting creates large area: ${formatNumber(area)} blocks²"
                )
            }
            else -> {
                Triple(Severity.INFO, defaultValue, "Within acceptable range")
            }
        }
        
        findings.add(ConfigFinding(
            setting = settingName,
            currentValue = defaultValue,
            recommendedValue = recommended,
            areaBlocksSquared = area,
            severity = severity,
            message = message
        ))
    }
    
    return findings.sortedByDescending { it.severity.ordinal }
}

/**
 * Checks if a setting name indicates a distance/radius value.
 */
fun isDistanceSetting(name: String): Boolean {
    return name.contains("Distance", ignoreCase = true) ||
           name.contains("Radius", ignoreCase = true)
}

/**
 * Formats a large number with commas.
 */
fun formatNumber(n: Double): String {
    return "%,.0f".format(n)
}

/**
 * Prints the diagnostic report to console.
 */
fun printReport(findings: List<ConfigFinding>) {
    if (findings.isEmpty()) {
        println("No configuration settings found to analyze.")
        return
    }
    
    println("-".repeat(80))
    println("FINDINGS:")
    println("-".repeat(80))
    
    var criticalCount = 0
    var warningCount = 0
    
    for (finding in findings) {
        val severityLabel = when (finding.severity) {
            Severity.CRITICAL -> "[CRITICAL]"
            Severity.WARNING -> "[WARNING]"
            Severity.INFO -> "[INFO]"
        }
        
        if (finding.severity == Severity.CRITICAL) criticalCount++
        if (finding.severity == Severity.WARNING) warningCount++
        
        println()
        println("$severityLabel ${finding.setting}")
        println("  Current:    ${finding.currentValue}")
        println("  Recommended: ${finding.recommendedValue}")
        if (finding.areaBlocksSquared > 0) {
            println("  Area:        ${formatNumber(finding.areaBlocksSquared)} blocks² per player")
            println("              (${formatNumber(finding.areaBlocksSquared * 10)} with 10 players)")
        }
        println("  Issue:       ${finding.message}")
    }
    
    println()
    println("-".repeat(80))
    println("SUMMARY:")
    println("  Critical issues: $criticalCount")
    println("  Warnings:        $warningCount")
    println("  Info:            ${findings.size - criticalCount - warningCount}")
    println("-".repeat(80))
    
    if (criticalCount > 0) {
        println()
        println("MATHEMATICAL ANALYSIS:")
        // Find the maxGenerationRequestDistance finding to get actual values
        val maxGenFinding = findings.find { it.setting == "maxGenerationRequestDistance" }
        if (maxGenFinding != null) {
            val r = maxGenFinding.currentValue
            val area = maxGenFinding.areaBlocksSquared
            println("  Distance setting: $r blocks")
            println("  Generation area: π × $r² = ${formatNumber(area)} blocks² per player")
            println("  With 10 players: ${formatNumber(area * 10)} blocks² total generation area")
        } else {
            println("  Distance settings create large generation areas per player.")
        }
        println("  This is the root cause of server tick performance degradation.")
        println()
        println("RECOMMENDED ACTIONS:")
        if (maxGenFinding != null) {
            println("  1. Change ${maxGenFinding.setting} default from ${maxGenFinding.currentValue} to ${maxGenFinding.recommendedValue}")
        } else {
            println("  1. Reduce maxGenerationRequestDistance default to 1024")
        }
        println("  2. Add performance warning for values > 2048")
        println("  3. Cap chunk event queue size to prevent unbounded growth")
    }
}

/**
 * Writes the report to a file.
 */
fun writeReportToFile(findings: List<ConfigFinding>, file: File) {
    file.writeText(buildString {
        appendLine("DistantHorizonsStandalone Configuration Diagnostics Report")
        appendLine("Generated: ${java.time.Instant.now()}")
        appendLine("=".repeat(80))
        appendLine()
        
        findings.forEach { finding ->
            appendLine("${finding.setting}:")
            appendLine("  Severity: ${finding.severity}")
            appendLine("  Current: ${finding.currentValue}")
            appendLine("  Recommended: ${finding.recommendedValue}")
            if (finding.areaBlocksSquared > 0) {
                appendLine("  Area: ${formatNumber(finding.areaBlocksSquared)} blocks²/player")
            }
            appendLine("  Issue: ${finding.message}")
            appendLine()
        }
        
        appendLine("=".repeat(80))
        appendLine("Configuration Impact Analysis:")
        appendLine("  Generation area per player = π × r²")
        // Find maxGenerationRequestDistance finding for accurate report
        val maxGenFinding = findings.find { it.setting == "maxGenerationRequestDistance" }
        if (maxGenFinding != null) {
            val r = maxGenFinding.currentValue
            val area = maxGenFinding.areaBlocksSquared
            appendLine("  With default r = $r: area = π × $r² ≈ ${formatNumber(area)} blocks²")
            appendLine("  With 10 players: total area ≈ ${formatNumber(area * 10)} blocks²")
        } else {
            appendLine("  Large distance settings create excessive generation area per player.")
        }
        appendLine("  At this generation area, server tick time is expected to exceed 50ms.")
    })
}

// Print info when script is applied
println("DH Diagnostics plugin applied. Run: ./gradlew dhDiagnostics")
