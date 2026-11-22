-- Labels and numbering belong to the Markdown. Shape identifies each role.
local styles = {
  ['tb-definition'] = 'teachingdefinition', ['tb-model'] = 'teachingdefinition',
  ['tb-assumption'] = 'teachingdefinition', ['tb-law'] = 'teachingdefinition',
  ['tb-result'] = 'teachingresult', ['tb-example'] = 'teachingexample',
  ['tb-counterexample'] = 'teachingexample'
}
function Div(div)
  if not FORMAT:match('latex') then return nil end
  local environment = nil
  local is_object = false
  for _, class in ipairs(div.classes) do
    if class:match('^tb%-') then is_object = true end
    if styles[class] then environment = styles[class] end
  end
  if not is_object then return nil end
  local start = '\\Needspace{8\\baselineskip}\n'
  if div.classes:includes('keep-first-display') then
    start = '\\Needspace{11\\baselineskip}\n'
  end
  if environment then start = start .. '\\begin{' .. environment .. '}\n' end
  if div.identifier ~= '' then
    start = start .. '\\hypertarget{' .. div.identifier .. '}{}\n'
  end
  local blocks = pandoc.Blocks{pandoc.RawBlock('latex', start)}
  blocks:extend(div.content)
  if environment then
    blocks:insert(pandoc.RawBlock('latex', '\\end{' .. environment .. '}'))
  end
  return blocks
end
