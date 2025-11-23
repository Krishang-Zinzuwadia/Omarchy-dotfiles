local M = {}

function M.setup()
    vim.cmd("hi clear")
    if vim.fn.exists("syntax_on") then vim.cmd("syntax reset") end

    vim.g.colors_name = "akane"
    vim.o.background = "dark"

    require("akane.theme").apply()
end

return M
