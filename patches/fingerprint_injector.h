// Copyright 2024 The Chromium Authors
// Fingerprint Injector - Kernel-level fingerprint injection system

#ifndef CONTENT_BROWSER_FINGERPRINT_INJECTOR_H_
#define CONTENT_BROWSER_FINGERPRINT_INJECTOR_H_

#include <string>
#include <vector>
#include "base/values.h"

namespace content {

// 指纹注入器 - 单例模式
// 在Chromium启动时加载配置文件，为所有指纹API提供统一的数据源
class FingerprintInjector {
 public:
  static FingerprintInjector* GetInstance();
  
  // 初始化 - 从命令行参数读取配置文件
  // chrome.exe --fingerprint-config=config.json
  bool Initialize();
  
  bool IsInitialized() const { return initialized_; }
  
  // ============ 硬件指纹 API ============
  
  // CPU
  int GetCPUCores() const;
  int GetCPUThreads() const;
  std::string GetCPUModel() const;
  
  // 内存
  int GetMemoryGB() const;
  
  // GPU
  std::string GetGPUVendor() const;
  std::string GetGPURenderer() const;
  std::string GetGPUDriverVersion() const;
  
  // 屏幕
  int GetScreenWidth() const;
  int GetScreenHeight() const;
  int GetColorDepth() const;
  int GetPixelDepth() const;
  
  // ============ Navigator 指纹 API ============
  
  std::string GetUserAgent() const;
  std::string GetPlatform() const;
  std::string GetVendor() const;
  std::string GetLanguage() const;
  std::vector<std::string> GetLanguages() const;
  
  // ============ WebGL 指纹 API ============
  
  std::string GetWebGLVendor() const;
  std::string GetWebGLRenderer() const;
  std::string GetWebGLVersion() const;
  std::string GetWebGLShadingLanguageVersion() const;
  std::vector<std::string> GetWebGLExtensions() const;
  
  // ============ Canvas/Audio 噪声种子 ============
  
  std::string GetCanvasNoiseSeed() const;
  std::string GetAudioNoiseSeed() const;
  
  // ============ 时区和地理位置 ============
  
  std::string GetTimezone() const;
  double GetGeolocationLatitude() const;
  double GetGeolocationLongitude() const;
  
  // ============ 字体列表 ============
  
  std::vector<std::string> GetFontList() const;
  
  // ============ WebRTC IP ============
  
  std::string GetWebRTCLocalIP() const;
  bool ShouldBlockWebRTC() const;
  
 private:
  FingerprintInjector();
  ~FingerprintInjector();
  
  // 禁止拷贝
  FingerprintInjector(const FingerprintInjector&) = delete;
  FingerprintInjector& operator=(const FingerprintInjector&) = delete;
  
  static FingerprintInjector* instance_;
  
  bool initialized_ = false;
  base::Value config_;  // JSON配置数据
};

}  // namespace content

#endif  // CONTENT_BROWSER_FINGERPRINT_INJECTOR_H_
