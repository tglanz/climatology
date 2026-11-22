-- Unnumbered chapters also own their running headers.
function Header(h)
  if FORMAT:match('latex') and h.level == 2 and pandoc.utils.stringify(h.content) == 'Exercises' then
    return {pandoc.RawBlock('latex', '\\Needspace{16\\baselineskip}'), h}
  end
  if FORMAT:match('latex') and h.level == 3 then
    return {pandoc.RawBlock('latex', '\\Needspace{12\\baselineskip}'), h}
  end
  if h.level == 1 and h.classes:includes('unnumbered') and FORMAT:match('latex') then
    local title = pandoc.utils.stringify(h.content):gsub('[{}]', ''):gsub('&', '\\&')
    return {h, pandoc.RawBlock('latex', '\\markboth{' .. title .. '}{' .. title .. '}')}
  end
end

-- Keep each short chapter summary together across page breaks.
function Pandoc(doc)
  if not FORMAT:match('latex') then return doc end
  local visible = pandoc.List()
  local omit = false
  for _, b in ipairs(doc.blocks) do
    if b.t == 'RawBlock' and b.text:match('markdown%-toc:start') then
      omit = true
    elseif b.t == 'RawBlock' and b.text:match('markdown%-toc:end') then
      omit = false
    elseif not omit then
      visible:insert(b)
    end
  end
  doc.blocks = visible
  local out = pandoc.List()
  local i = 1
  while i <= #doc.blocks do
    local b = doc.blocks[i]
    if b.t == 'Header' and b.level == 2 and pandoc.utils.stringify(b.content) == 'Chapter summary' then
      out:insert(pandoc.RawBlock('latex', '\\begin{samepage}'))
      out:insert(b)
      i = i + 1
      if i <= #doc.blocks then out:insert(doc.blocks[i]) end
      out:insert(pandoc.RawBlock('latex', '\\end{samepage}'))
    else
      out:insert(b)
    end
    i = i + 1
  end
  doc.blocks = out
  return doc
end
