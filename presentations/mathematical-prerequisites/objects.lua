-- Keep the Markdown labels authoritative; this filter supplies PDF typography.
local environments = {
  ['tb-definition']='tbdefinition', ['tb-assumption']='tbdefinition',
  ['tb-model']='tbdefinition', ['tb-law']='tbdefinition',
  ['tb-result']='tbresult', ['tb-example']='tbexample',
  ['tb-counterexample']='tbexample'
}
function Div(el)
  if not FORMAT:match('latex') then return nil end
  local teaching = false
  for _, class in ipairs(el.classes) do
    if class:match('^tb%-') then teaching = true end
  end
  if not teaching then return nil end
  local env = nil
  for _, class in ipairs(el.classes) do
    if environments[class] then env = environments[class] end
  end
  local before = '\\Needspace{4\\baselineskip}\n'
  if env then before = before .. '\\begin{' .. env .. '}\n' end
  if el.identifier ~= '' then
    before = before .. '\\hypertarget{' .. el.identifier .. '}{}\n'
  end
  local blocks = pandoc.Blocks{pandoc.RawBlock('latex', before)}
  blocks:extend(el.content)
  if env then blocks:insert(pandoc.RawBlock('latex', '\\end{' .. env .. '}')) end
  return blocks
end
