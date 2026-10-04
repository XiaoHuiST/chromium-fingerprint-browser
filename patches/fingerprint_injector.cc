// Copyright 2024 The Chromium Authors
// Fingerprint Injector Implementation

#include "content/browser/fingerprint_injector.h"

#include <fstream>
#include <memory>
#include "base/files/file_util.h"
#include "base/json/json_reader.h"
#include "base/logging.h"
#include "base/command_line.h"
#include "base/strings/string_number_conversions.h"

namespace content {

// 静态单例
FingerprintInjector* FingerprintInjector::instance_ = nullptr;

FingerprintInjector::FingerprintInjector() = default;
FingerprintInjector::~FingerprintInjector() = default;

// 获取单例
FingerprintInjector* FingerprintInjector::GetInstance() {
  if (!instance_) {
    instance_ = new FingerprintInjector();
  }
  return instance_;
}

// 初始化 - 从命令行读取配置
bool FingerprintInjector::Initialize() {
  base::CommandLine* cmd_line = base::CommandLine::ForCurrentProcess();
  
  if (!cmd_line->HasSwitch("fingerprint-config")) {
    LOG(WARNING) << "No fingerprint config specified, using default behavior";
    return false;
  }

  base::FilePath config_path = cmd_line->GetSwitchValuePath("fingerprint-config");
  
  std::string config_json;
  if (!base::ReadFileToString(config_path, &config_json)) {
    LOG(ERROR) << "Failed to read fingerprint config: " << config_path;
    return false;
  }

  // 解析 JSON
  auto parsed = base::JSONReader::ReadAndReturnValueWithError(config_json);
  if (!parsed.has_value()) {
    LOG(ERROR) << "Failed to parse fingerprint JSON: " << parsed.error().message;
    return false;
  }

  config_ = std::move(parsed.value());
  initialized_ = true;
  
  LOG(INFO) << "Fingerprint config loaded successfully from: " << config_path;
  return true;
}

// ============ 硬件指纹 API 实现 ============

int FingerprintInjector::GetCPUCores() const {
  if (!initialized_) return 0;
  const base::Value* value = config_.FindPath("hardware.cpu_cores");
  return value && value->is_int() ? value->GetInt() : 0;
}

int FingerprintInjector::GetCPUThreads() const {
  if (!initialized_) return 0;
  const base::Value* value = config_.FindPath("hardware.cpu_threads");
  return value && value->is_int() ? value->GetInt() : 0;
}

std::string FingerprintInjector::GetCPUModel() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("hardware.cpu_model");
  return value && value->is_string() ? value->GetString() : "";
}

int FingerprintInjector::GetMemoryGB() const {
  if (!initialized_) return 0;
  const base::Value* value = config_.FindPath("hardware.memory_gb");
  return value && value->is_int() ? value->GetInt() : 0;
}

std::string FingerprintInjector::GetGPUVendor() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("hardware.gpu_vendor");
  return value && value->is_string() ? value->GetString() : "";
}

std::string FingerprintInjector::GetGPURenderer() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("hardware.gpu_renderer");
  return value && value->is_string() ? value->GetString() : "";
}

std::string FingerprintInjector::GetGPUDriverVersion() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("hardware.gpu_driver");
  return value && value->is_string() ? value->GetString() : "";
}

int FingerprintInjector::GetScreenWidth() const {
  if (!initialized_) return 0;
  const base::Value* value = config_.FindPath("hardware.screen_width");
  return value && value->is_int() ? value->GetInt() : 0;
}

int FingerprintInjector::GetScreenHeight() const {
  if (!initialized_) return 0;
  const base::Value* value = config_.FindPath("hardware.screen_height");
  return value && value->is_int() ? value->GetInt() : 0;
}

int FingerprintInjector::GetColorDepth() const {
  if (!initialized_) return 24;
  const base::Value* value = config_.FindPath("hardware.color_depth");
  return value && value->is_int() ? value->GetInt() : 24;
}

int FingerprintInjector::GetPixelDepth() const {
  if (!initialized_) return 24;
  const base::Value* value = config_.FindPath("hardware.pixel_depth");
  return value && value->is_int() ? value->GetInt() : 24;
}

// ============ Navigator 指纹 API 实现 ============

std::string FingerprintInjector::GetUserAgent() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("navigator.userAgent");
  return value && value->is_string() ? value->GetString() : "";
}

std::string FingerprintInjector::GetPlatform() const {
  if (!initialized_) return "Win32";
  const base::Value* value = config_.FindPath("navigator.platform");
  return value && value->is_string() ? value->GetString() : "Win32";
}

std::string FingerprintInjector::GetVendor() const {
  if (!initialized_) return "Google Inc.";
  const base::Value* value = config_.FindPath("navigator.vendor");
  return value && value->is_string() ? value->GetString() : "Google Inc.";
}

std::string FingerprintInjector::GetLanguage() const {
  if (!initialized_) return "zh-CN";
  const base::Value* value = config_.FindPath("navigator.language");
  return value && value->is_string() ? value->GetString() : "zh-CN";
}

std::vector<std::string> FingerprintInjector::GetLanguages() const {
  std::vector<std::string> languages;
  if (!initialized_) {
    languages.push_back("zh-CN");
    return languages;
  }
  
  const base::Value* value = config_.FindPath("navigator.languages");
  if (value && value->is_list()) {
    for (const auto& lang : value->GetList()) {
      if (lang.is_string()) {
        languages.push_back(lang.GetString());
      }
    }
  }
  
  if (languages.empty()) {
    languages.push_back("zh-CN");
  }
  
  return languages;
}

// ============ WebGL 指纹 API 实现 ============

std::string FingerprintInjector::GetWebGLVendor() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("webgl.vendor");
  return value && value->is_string() ? value->GetString() : "";
}

std::string FingerprintInjector::GetWebGLRenderer() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("webgl.renderer");
  return value && value->is_string() ? value->GetString() : "";
}

std::string FingerprintInjector::GetWebGLVersion() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("webgl.version");
  return value && value->is_string() ? value->GetString() : "";
}

std::string FingerprintInjector::GetWebGLShadingLanguageVersion() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("webgl.shadingLanguageVersion");
  return value && value->is_string() ? value->GetString() : "";
}

std::vector<std::string> FingerprintInjector::GetWebGLExtensions() const {
  std::vector<std::string> extensions;
  if (!initialized_) return extensions;
  
  const base::Value* value = config_.FindPath("webgl.extensions");
  if (value && value->is_list()) {
    for (const auto& ext : value->GetList()) {
      if (ext.is_string()) {
        extensions.push_back(ext.GetString());
      }
    }
  }
  
  return extensions;
}

// ============ Canvas/Audio 噪声种子 实现 ============

std::string FingerprintInjector::GetCanvasNoiseSeed() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("canvas_noise_seed");
  return value && value->is_string() ? value->GetString() : "";
}

std::string FingerprintInjector::GetAudioNoiseSeed() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("audio_noise_seed");
  return value && value->is_string() ? value->GetString() : "";
}

// ============ 时区和地理位置 实现 ============

std::string FingerprintInjector::GetTimezone() const {
  if (!initialized_) return "Asia/Shanghai";
  const base::Value* value = config_.FindPath("timezone");
  return value && value->is_string() ? value->GetString() : "Asia/Shanghai";
}

double FingerprintInjector::GetGeolocationLatitude() const {
  if (!initialized_) return 39.9042;
  const base::Value* value = config_.FindPath("geolocation.latitude");
  return value && value->is_double() ? value->GetDouble() : 39.9042;
}

double FingerprintInjector::GetGeolocationLongitude() const {
  if (!initialized_) return 116.4074;
  const base::Value* value = config_.FindPath("geolocation.longitude");
  return value && value->is_double() ? value->GetDouble() : 116.4074;
}

// ============ 字体列表 实现 ============

std::vector<std::string> FingerprintInjector::GetFontList() const {
  std::vector<std::string> fonts;
  if (!initialized_) return fonts;
  
  const base::Value* value = config_.FindPath("fonts");
  if (value && value->is_list()) {
    for (const auto& font : value->GetList()) {
      if (font.is_string()) {
        fonts.push_back(font.GetString());
      }
    }
  }
  
  return fonts;
}

// ============ WebRTC IP 实现 ============

std::string FingerprintInjector::GetWebRTCLocalIP() const {
  if (!initialized_) return "";
  const base::Value* value = config_.FindPath("webrtc.local_ip");
  return value && value->is_string() ? value->GetString() : "";
}

bool FingerprintInjector::ShouldBlockWebRTC() const {
  if (!initialized_) return false;
  const base::Value* value = config_.FindPath("webrtc.block");
  return value && value->is_bool() ? value->GetBool() : false;
}

}  // namespace content
