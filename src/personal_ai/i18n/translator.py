from personal_ai.i18n.language import Language

_TRANSLATIONS: dict[str, dict[Language, str]] = {
    "title": {
        Language.VI: "PERSONAL AI 0.1.0 - DEMO TƯƠNG TÁC",
        Language.EN: "PERSONAL AI 0.1.0 - INTERACTIVE DEMO",
        Language.ZH: "PERSONAL AI 0.1.0 - 交互式演示",
    },
    "provider": {
        Language.VI: "Nhà cung cấp",
        Language.EN: "Provider",
        Language.ZH: "提供商",
    },
    "security": {
        Language.VI: "Bảo mật",
        Language.EN: "Security",
        Language.ZH: "安全",
    },
    "deny_by_default": {
        Language.VI: "từ chối mặc định",
        Language.EN: "deny-by-default",
        Language.ZH: "默认拒绝",
    },
    "commands": {
        Language.VI: "Lệnh:",
        Language.EN: "Commands:",
        Language.ZH: "命令：",
    },
    "help": {
        Language.VI: "Hiển thị trợ giúp",
        Language.EN: "Show commands",
        Language.ZH: "显示帮助",
    },
    "security_command": {
        Language.VI: "Kiểm tra quyền bảo mật",
        Language.EN: "Check permission boundary",
        Language.ZH: "检查权限边界",
    },
    "config": {
        Language.VI: "Xem cấu hình hệ thống",
        Language.EN: "Show runtime configuration",
        Language.ZH: "显示运行时配置",
    },
    "session": {
        Language.VI: "Xem phiên hội thoại",
        Language.EN: "Show current conversation",
        Language.ZH: "显示当前会话",
    },
    "clear": {
        Language.VI: "Bắt đầu phiên hội thoại mới",
        Language.EN: "Start a new conversation",
        Language.ZH: "开始新的会话",
    },
    "self_test": {
        Language.VI: "Chạy kiểm tra hệ thống",
        Language.EN: "Run release smoke tests",
        Language.ZH: "运行发布测试",
    },
    "language": {
        Language.VI: "Đổi ngôn ngữ",
        Language.EN: "Change language",
        Language.ZH: "切换语言",
    },
    "exit": {
        Language.VI: "Thoát",
        Language.EN: "Quit",
        Language.ZH: "退出",
    },
    "input_hint": {
        Language.VI: "Nhập tin nhắn để gửi tới Agent.",
        Language.EN: "Type any message to send it to the Agent.",
        Language.ZH: "输入消息发送给 Agent。",
    },
    "goodbye": {
        Language.VI: "Tạm biệt.",
        Language.EN: "Goodbye.",
        Language.ZH: "再见。",
    },
    "session_cleared": {
        Language.VI: "Đã tạo phiên hội thoại mới.",
        Language.EN: "Session cleared.",
        Language.ZH: "会话已清除。",
    },
    "runtime_configuration": {
        Language.VI: "Cấu hình runtime",
        Language.EN: "Runtime configuration",
        Language.ZH: "运行时配置",
    },
    "fake_llm_enabled": {
        Language.VI: "Fake LLM được bật",
        Language.EN: "Fake LLM enabled",
        Language.ZH: "Fake LLM 已启用",
    },
    "provider_mode": {
        Language.VI: "Chế độ provider",
        Language.EN: "Provider mode",
        Language.ZH: "提供商模式",
    },
    "security_boundary": {
        Language.VI: "Biên bảo mật",
        Language.EN: "Security boundary",
        Language.ZH: "安全边界",
    },
    "filesystem_read": {
        Language.VI: "Quyền đọc filesystem",
        Language.EN: "Filesystem read permission",
        Language.ZH: "文件系统读取权限",
    },
    "filesystem_denied": {
        Language.VI: "quyền đọc filesystem bị từ chối mặc định.",
        Language.EN: "filesystem read is denied by default.",
        Language.ZH: "文件系统读取默认被拒绝。",
    },
    "filesystem_not_denied": {
        Language.VI: "quyền đọc filesystem không bị từ chối.",
        Language.EN: "filesystem read is not denied.",
        Language.ZH: "文件系统读取未被拒绝。",
    },
    "conversation_session": {
        Language.VI: "Phiên hội thoại",
        Language.EN: "Conversation session",
        Language.ZH: "会话",
    },
    "empty": {
        Language.VI: "(trống)",
        Language.EN: "(empty)",
        Language.ZH: "（空）",
    },
    "check_fake_llm": {
        Language.VI: "Fake LLM được bật",
        Language.EN: "Fake LLM enabled",
        Language.ZH: "Fake LLM 已启用",
    },
    "check_filesystem": {
        Language.VI: "Filesystem read bị từ chối",
        Language.EN: "Filesystem read denied",
        Language.ZH: "文件系统读取被拒绝",
    },
    "check_agent_response": {
        Language.VI: "Agent trả về response",
        Language.EN: "Agent returned response",
        Language.ZH: "Agent 返回响应",
    },
    "check_fake_response": {
        Language.VI: "Response đúng là fake response",
        Language.EN: "Expected fake response",
        Language.ZH: "响应符合预期",
    },
    "check_assistant_message": {
        Language.VI: "Assistant message được ghi nhận",
        Language.EN: "Assistant message recorded",
        Language.ZH: "助手消息已记录",
    },
    "check_data_isolation": {
        Language.VI: "Không tạo dữ liệu ngoài ý muốn",
        Language.EN: "No unexpected demo data",
        Language.ZH: "未创建意外演示数据",
    },
    "pass": {
        Language.VI: "ĐẠT",
        Language.EN: "PASS",
        Language.ZH: "通过",
    },
    "fail": {
        Language.VI: "THẤT BẠI",
        Language.EN: "FAIL",
        Language.ZH: "失败",
    },
    "warning": {
        Language.VI: "CẢNH BÁO",
        Language.EN: "WARNING",
        Language.ZH: "警告",
    },
    "self_test_result": {
        Language.VI: "KẾT QUẢ KIỂM TRA",
        Language.EN: "SELF TEST RESULT",
        Language.ZH: "自检结果",
    },
    "language_selection": {
        Language.VI: "Chọn ngôn ngữ",
        Language.EN: "Language selection",
        Language.ZH: "语言选择",
    },
    "language_changed": {
        Language.VI: "Đã đổi ngôn ngữ sang Tiếng Việt.",
        Language.EN: "Language changed to English.",
        Language.ZH: "语言已切换为中文。",
    },
    "unsupported_language": {
        Language.VI: "Ngôn ngữ không được hỗ trợ.",
        Language.EN: "Unsupported language.",
        Language.ZH: "不支持的语言。",
    },
    "error": {
        Language.VI: "LỖI",
        Language.EN: "ERROR",
        Language.ZH: "错误",
    },
}


class Translator:
    def __init__(self, language: Language) -> None:
        if not isinstance(language, Language):
            raise ValueError("language must be a Language")

        self.language = language

    def translate(self, key: str) -> str:
        try:
            translations = _TRANSLATIONS[key]
        except KeyError as exc:
            raise KeyError(f"unknown translation key: {key}") from exc

        return translations[self.language]

    def __call__(self, key: str) -> str:
        return self.translate(key)
