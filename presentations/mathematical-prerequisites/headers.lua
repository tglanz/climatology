-- Unnumbered report chapters do not set running marks themselves.
local chapter = 0
function Header(el)
  if el.level == 1 and not el.classes:includes('unnumbered') then chapter = chapter + 1 end
  if FORMAT:match('latex') and chapter == 12 and el.level == 2 and
      pandoc.utils.stringify(el.content) == 'Chapter summary and self-test' then
    return {pandoc.RawBlock('latex', '\\Needspace{16\\baselineskip}'), el}
  end
  if FORMAT:match('latex') and el.level == 1 and el.classes:includes('unnumbered') then
    local title = pandoc.utils.stringify(el.content)
    local subtitles = {['Scope and source conventions']='Reading route and conventions',
                       ['Self-test answers']='Solutions by chapter',
                       ['Repository reading map']='Applications of the theory',
                       ['References']='Original sources'}
    return {el, pandoc.RawBlock('latex', '\\markboth{' .. title .. '}{' .. (subtitles[title] or title) .. '}')}
  end
end
