/** Website 分类配置 */
const WEBSITE_SORTS: WebsiteSort[] = [
  {
    title: "工具",
    sites: [
      {
        title: "图片网站索引",
        url: "https://elysia.freeddns.org/",
        icon: "/assets/Only-index.svg",
        color: "#0171CD",
      },
      {
        title: "ChatGPT-Next-Chat",
        description: "",
        url: "https://bronya.giize.com/",
        icon: "/assets/ChatGPT-Next-Chat.svg",
      },
      {
        title: "Lolicon APP",
        description: "",
        url: "https://jyf0214.giize.com/",
        icon: "/assets/Lolicon-APP.svg",
      },
    ],
  },
  {
    title: "友情链接",
    sites: [
      {
        title: "Jyf0214 Blog",
        description: "Jyf0214 的博客",
        url: "https://elysia.camdvr.org",
        icon: "/assets/logo.svg",
      },
    ],
  },
];

/** Website 配置（2023.3.29 已废弃） */
const WEBSITE_ITEMS: WebsiteItem[] = [];

const GLOBAL_CONFIG = {
  /**
   * 博客名称
   */
  BLOG_NAME: "Jyf0214-Blog",
  /**
   * 个人博客链接
   */
  BLOG_URL: "https://elysia.camdvr.org/",
  /**
   * 指定中心 LOGO 图片地址
   */
  LOGO_URL: null,
  /**
   * 个人 Github 链接
   */
  GITHUB_URL: "https://github.com/Jyf0214",
  /**
   * 背景图片地址
   */
  BACKGROUND_IMG_URL: "https://bing.img.run/1920x1080.php",
  /**
   * ICP 备案号，留空不显示
   */
  ICP: "",
  ICP_URL: "https://beian.miit.gov.cn/",
  FOOTER_INFO: true,
  /**
   * 网站欢迎标语
   */
  SLOGANS: [
    "欢迎拜访",
    "歡迎拜訪",
    "Welcome, my friend!",
    "訪問へようこそ",
    "嗨，别来无恙",
    "不忘初心，一生浪漫",
    "最近还好吗？",
    "流星，落花，萤火",
    "马车越空，晃荡越响",
  ],
  /**
   * Website 分类配置
   */
  WEBSITE_SORTS,
  /**
   * Website 配置（2023.3.29 已废弃）
   */
  WEBSITE_ITEMS,
  /**
   * 网站 Title Keywords Description 的配置，用于 SEO
   */
  TKD: {
    title: "Jyf0214's Blog Index",
    keywords: "Blog, Index, Index Page, Jyf0214",
    description: "This is Jyf0214's personal blog index page.",
  },
};

export default GLOBAL_CONFIG;
