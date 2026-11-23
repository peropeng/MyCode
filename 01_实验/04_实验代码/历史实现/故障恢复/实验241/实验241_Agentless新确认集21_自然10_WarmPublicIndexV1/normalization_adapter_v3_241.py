"""Conservative generic old-source AST guard; original normalization remains intact."""
import ast

def install(official):
 original=official.is_just_new_function
 if getattr(original,'_scope3_old_ast_guard',False):return original
 def guarded_is_just_new_function(old_code,new_code):
  try:ast.parse(old_code)
  except SyntaxError:
   # Invalid new code is still rejected. Without an old AST, adding functions
   # cannot be proven, so preserve the full original normalized diff context.
   ast.parse(new_code)
   return False
  return original(old_code,new_code)
 guarded_is_just_new_function._scope3_old_ast_guard=True
 guarded_is_just_new_function._original_is_just_new_function=original
 official.is_just_new_function=guarded_is_just_new_function
 return guarded_is_just_new_function
