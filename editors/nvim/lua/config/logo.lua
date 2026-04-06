local logo_path = vim.env.LOGO

return table.concat(vim.fn.readfile(logo_path), "\n ")
