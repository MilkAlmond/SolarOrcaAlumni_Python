// ============================================
// 主题与国际化（i18n）
// 功能：主题切换、多语言支持
// ============================================

// ==================== 常量定义 ====================

/**
 * 主题名称映射表（支持中英文）
 * 用于在UI上显示当前主题的名称
 */
const THEME_NAMES = {
    en: {
        ocean: 'Ocean Breeze',
        fall: 'Fall Forest',
        midnight: 'Midnight',
        blossom: 'Blossom',
        custom: 'Custom Theme'
    },
    zh: {
        ocean: '海洋之风',
        fall: '秋日森林',
        midnight: '午夜',
        blossom: '花开',
        custom: '自定义主题'
    }
};

// ==================== 辅助函数 ====================

/**
 * 获取当前语言偏好
 * @returns {string} 语言代码（'zh' 或 'en'），默认为 'en'
 */
const getCurrentLanguage = () => localStorage.getItem('selectedLanguage') || 'en';

/**
 * 获取当前主题
 * @returns {string} 主题名称，默认为 'ocean'
 */
const getCurrentTheme = () => localStorage.getItem('selectedTheme') || 'ocean';

/**
 * 记录错误日志到控制台
 * @param {string} context - 错误发生的上下文
 * @param {Error} error - 错误对象
 */
const logError = (context, error) => console.error(`Error in ${context}:`, error);

/** 判断元素是否为输入框 */
const isInputElement = (element) => element.tagName === 'INPUT';

/** 判断元素是否为按钮 */
const isButtonElement = (element) => element.tagName === 'BUTTON';

/** 判断元素是否为标题（H1/H2/H3） */
const isHeadingElement = (element) => ['H1', 'H2', 'H3'].includes(element.tagName);

/** 判断元素是否为表格表头 */
const isTableHeaderElement = (element) => element.tagName === 'TH';

/** 判断元素是否为文本域 */
const isTextAreaElement = (element) => element.tagName === 'TEXTAREA';

// ==================== 翻译/国际化函数 ====================

/**
 * 将翻译文本应用到单个DOM元素
 * 根据元素类型决定是设置innerHTML、value还是placeholder
 *
 * @param {HTMLElement} element - 目标DOM元素
 * @param {string} key - 翻译键名
 * @param {Object} translations - 翻译数据对象
 */
const applyTranslationToElement = (element, key, translations) => {
    if (!translations[key]) return;

    const inputType = isInputElement(element) ? element.type : null;

    // 支持带emoji图标的按钮，如 🌊 海洋之风
    if (isButtonElement(element)) {
        const iconMatch = element.innerHTML.match(/[🌊🍂🌙🌸🎨]/);
        const icon = iconMatch ? iconMatch[0] : '';
        const span = element.querySelector('span');

        if (icon && span) {
            span.innerHTML = translations[key];
            element.innerHTML = `${icon} ${span.outerHTML}`;
        } else if (icon) {
            element.innerHTML = `${icon} ${translations[key]}`;
        } else if (span) {
            span.innerHTML = translations[key];
        } else {
            element.innerHTML = translations[key];
        }
        return;
    }

    // ---------- 输入框按钮类型 ----------
    if (isInputElement(element) && (inputType === 'button' || inputType === 'submit')) {
        element.value = translations[key];
        return;
    }

    // ---------- 输入框占位符（text/email/password） ----------
    if (isInputElement(element) && (inputType === 'text' || inputType === 'email' || inputType === 'password')) {
        element.placeholder = translations[key];
        return;
    }

    // ---------- 文本域占位符 ----------
    if (isTextAreaElement(element)) {
        element.placeholder = translations[key];
        return;
    }

    // ---------- 标题和表头 ----------
    if (isHeadingElement(element) || isTableHeaderElement(element)) {
        element.innerHTML = translations[key];
        return;
    }

    // ---------- 默认：设置innerHTML ----------
    element.innerHTML = translations[key];
};

/**
 * 应用所有翻译到页面中带有data-i18n属性的元素
 *
 * @param {Object} translations - 翻译数据对象
 */
const applyTranslations = (translations) => {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        applyTranslationToElement(element, key, translations);
    });

    // 更新页面标题
    if (translations.page_title) {
        document.title = translations.page_title;
    }
};

/**
 * 加载指定语言的翻译文件并应用到页面
 *
 * @param {string} lang - 语言代码（'zh' 或 'en'）
 */
const loadLanguage = async (lang) => {
    try {
        // 使用绝对路径 /static/locales/
        const response = await fetch(`/static/locales/${lang}.json`);
        const translations = await response.json();

        applyTranslations(translations);
        localStorage.setItem('selectedLanguage', lang);
        document.documentElement.setAttribute('data-lang', lang);
        updateLanguageDisplay(lang);
        updateThemeDisplay(getCurrentTheme());
    } catch (error) {
        logError('loading language', error);
    }
};

/**
 * 切换语言（公开接口）
 * @param {string} lang - 语言代码
 */
const setLanguage = async (lang) => {
    await loadLanguage(lang);
};

/**
 * 更新UI上显示当前语言的文字
 * @param {string} lang - 语言代码
 */
const updateLanguageDisplay = (lang) => {
    const langNameElement = document.getElementById('currentLanguage');
    if (langNameElement) {
        langNameElement.innerText = lang === 'zh' ? '中文' : 'English';
    }
};

/** 加载保存的语言偏好（页面初始化时调用） */
const loadSavedLanguage = async () => {
    const savedLanguage = localStorage.getItem('selectedLanguage');
    await setLanguage(savedLanguage && savedLanguage !== 'en' ? savedLanguage : 'en');
};

// ==================== 主题函数 ====================

/**
 * 更新UI上显示当前主题的名称
 * @param {string} theme - 主题名称
 */
const updateThemeDisplay = (theme) => {
    const themeNameElement = document.getElementById('currentTheme');
    if (themeNameElement) {
        const currentLang = getCurrentLanguage();
        themeNameElement.innerText = THEME_NAMES[currentLang][theme] || THEME_NAMES.en[theme];
    }
};

/**
 * 加载自定义主题（从localStorage读取用户配置）
 * 自定义主题通过CSS变量直接覆盖，不设置data-theme属性
 */
const loadCustomTheme = () => {
    const customTheme = localStorage.getItem('customTheme');
    if (customTheme) {
        try {
            const theme = JSON.parse(customTheme);
            document.documentElement.style.setProperty('--primary', theme.primary);
            document.documentElement.style.setProperty('--secondary', theme.secondary);
            document.documentElement.style.setProperty('--background', theme.background);
            document.documentElement.style.setProperty('--card-bg', theme.cardBg);
            document.documentElement.style.setProperty('--text', theme.text);
            document.documentElement.removeAttribute('data-theme');
            updateThemeDisplay('custom');
        } catch (error) {
            logError('loading custom theme', error);
        }
    }
};

/**
 * 切换主题（公开接口）
 * @param {string} theme - 主题名称（ocean/fall/midnight/blossom/custom）
 */
const setTheme = (theme) => {
    if (theme === 'custom') {
        loadCustomTheme();
    } else {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('selectedTheme', theme);
        updateThemeDisplay(theme);
    }
};

/** 加载保存的主题偏好（页面初始化时调用） */
const loadSavedTheme = () => {
    const savedTheme = getCurrentTheme();
    const customTheme = localStorage.getItem('customTheme');

    if (savedTheme === 'custom' && customTheme) {
        loadCustomTheme();
    } else if (savedTheme !== 'custom') {
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeDisplay(savedTheme);
    } else {
        updateThemeDisplay('ocean');
    }
};

// ==================== 公共页面函数（无Session） ====================

/**
 * 公共页面的语言切换函数（用于未登录页面如login.jsp、signup.jsp等）
 * 与标准语言切换不同，此函数只切换页面显示，不依赖Session
 *
 * @param {string} lang - 语言代码
 */
const publicSetLanguage = async (lang) => {
    try {
        // 使用绝对路径 /static/locales/
        const response = await fetch(`/static/locales/${lang}.json`);
        const data = await response.json();

        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (data[key]) {
                applyTranslationToElement(el, key, data);
            }
        });

        localStorage.setItem('selectedLanguage', lang);
        document.documentElement.setAttribute('data-lang', lang);

        // 更新搜索框的占位符（如果存在）
        const searchInput = document.getElementById('searchInput');
        if (searchInput && data.search_questions) {
            searchInput.placeholder = data.search_questions;
        }
    } catch (error) {
        logError('public setLanguage', error);
    }
};

// ==================== 页面初始化 ====================

/**
 * 页面加载时执行初始化
 * 1. 加载保存的主题
 * 2. 加载保存的语言偏好（使用IIFE处理异步）
 */
loadSavedTheme();

// 使用立即执行函数表达式（IIFE）处理异步初始化，避免未处理的Promise
(async () => {
    await loadSavedLanguage();
})();

// ==================== 导出全局函数 ====================
// 将核心函数挂载到window对象，供全局调用（如HTML中的onclick）

/**
 * 公共页面语言切换函数（供未登录页面使用）
 * @example onclick="window.publicSetLanguage('en')"
 */
window.publicSetLanguage = publicSetLanguage;

/**
 * 主题切换函数
 * @example onclick="window.setTheme('ocean')"
 */
window.setTheme = setTheme;

/**
 * 语言切换函数（供已登录页面使用）
 * @example onclick="window.setLanguage('zh')"
 */
window.setLanguage = setLanguage;