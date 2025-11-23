local M = {}

-- Palette
M.palette = {
    bg     = "#0E1E36", -- oxford-blue
    fg     = "#F4B999", -- peach
    violet = "#9279AA", -- african-violet
    purple = "#574F72", -- english-violet
    mag    = "#763C5D", -- quinacridone-magenta
    rose   = "#BE6F76", -- old-rose
    blush  = "#C85670", -- blush
    coral  = "#FA7E75", -- coral-pink
    red    = "#D2495B", -- amaranth
    darkp  = "#4A2036", -- dark-purple
}

-- Apply highlights
function M.apply()
    local P = M.palette
    local hi = function(group, spec)
        vim.api.nvim_set_hl(0, group, spec)
    end

    vim.o.termguicolors = true

    -- UI
    hi("Normal", { fg = P.fg, bg = P.bg })
    hi("NormalNC", { fg = P.fg, bg = P.bg })
    hi("NormalFloat", { fg = P.fg, bg = P.bg })
    hi("FloatBorder", { fg = P.purple, bg = P.bg })
    hi("WinSeparator", { fg = P.darkp, bg = P.bg })
    hi("VertSplit", { fg = P.darkp, bg = P.bg })
    hi("LineNr", { fg = P.purple, bg = P.bg })
    hi("CursorLine", { bg = P.darkp })
    hi("CursorLineNr", { fg = P.fg, bold = true })
    hi("SignColumn", { bg = P.bg })
    hi("Visual", { bg = P.purple })
    hi("Search", { fg = P.bg, bg = P.violet, bold = true })
    hi("IncSearch", { fg = P.bg, bg = P.coral, bold = true })
    hi("MatchParen", { fg = P.coral, bold = true })
    hi("Pmenu", { fg = P.fg, bg = P.darkp })
    hi("PmenuSel", { fg = P.bg, bg = P.violet, bold = true })
    hi("PmenuThumb", { bg = P.violet })
    hi("StatusLine", { fg = P.fg, bg = P.purple })
    hi("StatusLineNC", { fg = P.purple, bg = P.darkp })
    hi("TabLine", { fg = P.fg, bg = P.darkp })
    hi("TabLineSel", { fg = P.bg, bg = P.violet, bold = true })
    hi("TabLineFill", { bg = P.bg })
    hi("Title", { fg = P.fg, bold = true })
    hi("Directory", { fg = P.violet, bold = true })
    hi("Whitespace", { fg = P.purple })

    -- Syntax
    hi("Comment", { fg = P.purple, italic = true })
    hi("Identifier", { fg = P.blush })
    hi("Function", { fg = P.violet, bold = true })
    hi("Statement", { fg = P.violet })
    hi("Conditional", { fg = P.violet })
    hi("Repeat", { fg = P.violet })
    hi("Operator", { fg = P.fg })
    hi("Keyword", { fg = P.violet, italic = true })
    hi("PreProc", { fg = P.fg })
    hi("Type", { fg = P.rose })
    hi("Special", { fg = P.blush })
    hi("Underlined", { fg = P.fg, underline = true })
    hi("Todo", { fg = P.bg, bg = P.fg, bold = true })
    hi("Constant", { fg = P.blush })
    hi("String", { fg = P.fg })
    hi("Character", { fg = P.fg })
    hi("Number", { fg = P.coral })
    hi("Boolean", { fg = P.coral })
    hi("Float", { fg = P.coral })

    -- Diagnostics
    hi("Error", { fg = P.red, bold = true })
    hi("WarningMsg", { fg = P.coral })
    hi("DiagnosticError", { fg = P.red })
    hi("DiagnosticWarn", { fg = P.fg })
    hi("DiagnosticInfo", { fg = P.violet })
    hi("DiagnosticHint", { fg = P.rose })
    hi("DiagnosticOk", { fg = P.rose })
    hi("DiagnosticUnderlineError", { undercurl = true, sp = P.red })
    hi("DiagnosticUnderlineWarn", { undercurl = true, sp = P.fg })
    hi("DiagnosticUnderlineInfo", { undercurl = true, sp = P.violet })
    hi("DiagnosticUnderlineHint", { undercurl = true, sp = P.rose })
    hi("DiagnosticVirtualTextError", { fg = P.red, bg = P.darkp })
    hi("DiagnosticVirtualTextWarn", { fg = P.fg, bg = P.darkp })
    hi("DiagnosticVirtualTextInfo", { fg = P.violet, bg = P.darkp })
    hi("DiagnosticVirtualTextHint", { fg = P.rose, bg = P.darkp })

    -- Git/Diff
    hi("DiffAdd", { fg = P.rose, bg = P.darkp })
    hi("DiffChange", { fg = P.violet, bg = P.darkp })
    hi("DiffDelete", { fg = P.red, bg = P.darkp })
    hi("DiffText", { fg = P.fg, bg = P.purple, bold = true })
    hi("GitSignsAdd", { fg = P.rose })
    hi("GitSignsChange", { fg = P.violet })
    hi("GitSignsDelete", { fg = P.red })

    -- Treesitter
    hi("@comment", { link = "Comment" })
    hi("@function", { link = "Function" })
    hi("@function.builtin", { link = "Function" })
    hi("@keyword", { link = "Keyword" })
    hi("@keyword.function", { link = "Keyword" })
    hi("@keyword.operator", { link = "Keyword" })
    hi("@type", { link = "Type" })
    hi("@type.builtin", { link = "Type" })
    hi("@string", { link = "String" })
    hi("@number", { link = "Number" })
    hi("@boolean", { link = "Boolean" })
    hi("@float", { link = "Float" })
    hi("@variable", { fg = P.fg })
    hi("@variable.builtin", { fg = P.blush, italic = true })
    hi("@constant", { link = "Constant" })
    hi("@constant.builtin", { link = "Constant" })
    hi("@punctuation", { fg = P.purple })
    hi("@punctuation.bracket", { fg = P.purple })
    hi("@punctuation.delimiter", { fg = P.purple })
    hi("@operator", { link = "Operator" })
    hi("@parameter", { fg = P.rose })
    hi("@property", { fg = P.rose })
    hi("@field", { fg = P.rose })
    hi("@constructor", { fg = P.violet })
    hi("@tag", { fg = P.violet })
    hi("@tag.attribute", { fg = P.rose })
    hi("@tag.delimiter", { fg = P.purple })

    -- LSP Semantic Tokens
    hi("@lsp.type.class", { link = "Type" })
    hi("@lsp.type.decorator", { link = "Function" })
    hi("@lsp.type.enum", { link = "Type" })
    hi("@lsp.type.enumMember", { link = "Constant" })
    hi("@lsp.type.function", { link = "Function" })
    hi("@lsp.type.interface", { link = "Type" })
    hi("@lsp.type.macro", { link = "Function" })
    hi("@lsp.type.method", { link = "Function" })
    hi("@lsp.type.namespace", { link = "Type" })
    hi("@lsp.type.parameter", { link = "@parameter" })
    hi("@lsp.type.property", { link = "@property" })
    hi("@lsp.type.struct", { link = "Type" })
    hi("@lsp.type.type", { link = "Type" })
    hi("@lsp.type.typeParameter", { link = "Type" })
    hi("@lsp.type.variable", { link = "@variable" })

    -- Telescope
    hi("TelescopeBorder", { fg = P.purple, bg = P.bg })
    hi("TelescopePromptBorder", { fg = P.violet, bg = P.bg })
    hi("TelescopeResultsBorder", { fg = P.purple, bg = P.bg })
    hi("TelescopePreviewBorder", { fg = P.purple, bg = P.bg })
    hi("TelescopeSelection", { fg = P.bg, bg = P.violet, bold = true })
    hi("TelescopeSelectionCaret", { fg = P.coral })
    hi("TelescopeMatching", { fg = P.coral, bold = true })
    hi("TelescopePromptPrefix", { fg = P.violet })

    -- Neo-tree
    hi("NeoTreeNormal", { fg = P.fg, bg = P.bg })
    hi("NeoTreeNormalNC", { fg = P.fg, bg = P.bg })
    hi("NeoTreeRootName", { fg = P.violet, bold = true })
    hi("NeoTreeDirectoryName", { fg = P.violet })
    hi("NeoTreeDirectoryIcon", { fg = P.violet })
    hi("NeoTreeFileNameOpened", { fg = P.coral })
    hi("NeoTreeIndentMarker", { fg = P.purple })
    hi("NeoTreeGitAdded", { fg = P.rose })
    hi("NeoTreeGitModified", { fg = P.violet })
    hi("NeoTreeGitDeleted", { fg = P.red })

    -- Which-key
    hi("WhichKey", { fg = P.violet, bold = true })
    hi("WhichKeyGroup", { fg = P.rose })
    hi("WhichKeyDesc", { fg = P.fg })
    hi("WhichKeySeparator", { fg = P.purple })
    hi("WhichKeyFloat", { bg = P.bg })

    -- Notify
    hi("NotifyERRORBorder", { fg = P.red })
    hi("NotifyWARNBorder", { fg = P.coral })
    hi("NotifyINFOBorder", { fg = P.violet })
    hi("NotifyDEBUGBorder", { fg = P.purple })
    hi("NotifyTRACEBorder", { fg = P.purple })
    hi("NotifyERRORIcon", { fg = P.red })
    hi("NotifyWARNIcon", { fg = P.coral })
    hi("NotifyINFOIcon", { fg = P.violet })
    hi("NotifyDEBUGIcon", { fg = P.purple })
    hi("NotifyTRACEIcon", { fg = P.purple })
    hi("NotifyERRORTitle", { fg = P.red })
    hi("NotifyWARNTitle", { fg = P.coral })
    hi("NotifyINFOTitle", { fg = P.violet })
    hi("NotifyDEBUGTitle", { fg = P.purple })
    hi("NotifyTRACETitle", { fg = P.purple })

    -- Indent Blankline
    hi("IblIndent", { fg = P.darkp })
    hi("IblScope", { fg = P.purple })

    -- Dashboard
    hi("DashboardShortCut", { fg = P.violet })
    hi("DashboardHeader", { fg = P.coral })
    hi("DashboardCenter", { fg = P.rose })
    hi("DashboardFooter", { fg = P.purple, italic = true })
end

return M
