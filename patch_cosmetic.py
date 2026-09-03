import re

with open('app/src/main/assets/extensions/remmi_engine_extension/cosmetic_filter.js', 'r') as f:
    content = f.read()

target = """        .catch((_e) => {
          isInflight = false;
          if (pendingClassesSet.size > 0 || pendingIdsSet.size > 0) {
            scheduleScan();
          }
        });"""

replacement = """        .catch((_e) => {
          isInflight = false;
          // Clear pending to prevent infinite retry loops on timeout
          pendingClassesSet.clear();
          pendingIdsSet.clear();
        });"""

content = content.replace(target, replacement)

with open('app/src/main/assets/extensions/remmi_engine_extension/cosmetic_filter.js', 'w') as f:
    f.write(content)
