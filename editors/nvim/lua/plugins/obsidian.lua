return {
  "epwalsh/obsidian.nvim",
  version = "*",
  lazy = true,
  ft = "markdown",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "nvim-telescope/telescope.nvim",
  },
  keys = {
    { "<leader>o", desc = "Obsidian" },
  },
  cmd = {
    "ObsidianOpen",
    "ObsidianNew",
    "ObsidianToday",
    "ObsidianYesterday",
    "ObsidianTomorrow",
    "ObsidianQuickSwitch",
    "ObsidianSearch",
    "ObsidianBacklinks",
    "ObsidianLinks",
    "ObsidianRename",
    "ObsidianPasteImg",
  },

  opts = {
    workspaces = {
      { name = "Learning", path = "~/Development/Learning" },
    },

    log_level = vim.log.levels.INFO,

    daily_notes = {
      folder = "journal/daily",
      date_format = "%Y-%m-%d",
      alias_format = "%B %-d, %Y",
      default_tags = { "daily", "journal" },
      template = "templates/daily.md",
    },

    -- Evita el error de `cmp` si no usas nvim-cmp
    completion = { nvim_cmp = false },

    templates = {
      folder = "templates",
      date_format = "%Y-%m-%d",
      time_format = "%H:%M",
      substitutions = {},
    },

    ui = { enable = true },

    picker = {
      name = "telescope.nvim",
    },
  },
}
