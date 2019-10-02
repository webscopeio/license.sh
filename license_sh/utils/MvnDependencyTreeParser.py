from anytree import AnyNode

def parse(tree_text):
  if not tree_text:
    return None
  raw_lines = tree_text.split('\n')
  root = parse_dependency(raw_lines[0], True)
  parent = root
  for raw_line in raw_lines[1:]:
    dependency = parse_dependency(raw_line)
    new_parent = parent
    while new_parent.level >= dependency.level:
      new_parent = new_parent.parent
    dependency.parent = new_parent
    parent = dependency
  return root

def get_dependency_level(raw_line):
  index = 0
  level = 0
  POS_LENGTH = 3
  while True:
    level += 1
    pos_string = raw_line[index : index+POS_LENGTH]
    if pos_string == '+- ' or pos_string == '\\- ':
      break
    
    index += POS_LENGTH
  return level

def parse_dependency(raw_line, root = False):
  raw_dependency = raw_line if root else raw_line.split('-', 1)[1].strip()
  dependency = raw_dependency.split(':')
  return AnyNode(
    name=dependency[1],
    version=dependency[3],
    level=(0 if root else get_dependency_level(raw_line))
  )