plugins {
    id("jacoco") // ✅ 加入 Jacoco Plugin
    alias(libs.plugins.android.application)
    alias(libs.plugins.jetbrains.kotlin.android)
}

android {
    namespace = "com.shawn.kubomi"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.shawn.kubomi"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.1"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
    tasks.register<JacocoReport>("jacocoTestReport") {
//        dependsOn("testDebugUnitTest") // or testStgDebugUnitTest

        reports {
            xml.required.set(true)
            html.required.set(true)
            csv.required.set(false)
        }
    }

//    tasks.register<JacocoReport>("jacocoTestReportDebug") {
//        dependsOn("testDebugUnitTest")
//
//        val fileFilter = listOf(
//            "**/R.class",
//            "**/R$*.class",
//            "**/BuildConfig.*",
//            "**/Manifest*.*",
//            "**/*Test*.*"
//        )
//
//        val debugTree = fileTree("${buildDir}/intermediates/javac/debug") {
//            exclude(fileFilter)
//        }
//
//        classDirectories.setFrom(debugTree)
//        sourceDirectories.setFrom(files("src/main/java", "src/main/kotlin"))
//        executionData.setFrom(fileTree(buildDir).include(
//            "jacoco/testDebugUnitTest.exec",
//            "outputs/unit_test_code_coverage/debugUnitTest/testDebugUnitTest.exec"
//        ))

}

dependencies {

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}