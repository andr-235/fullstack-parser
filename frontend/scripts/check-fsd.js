#!/usr/bin/env node

const fs = require('fs')
const path = require('path')
const glob = require('glob')

// FSD слои в порядке зависимостей
const FSD_LAYERS = [
  'app',
  'pages',
  'widgets',
  'features',
  'entities',
  'shared',
  'processes',
]

// Правила импортов между слоями
const IMPORT_RULES = {
  app: ['pages', 'widgets', 'features', 'entities', 'shared', 'processes'],
  pages: ['widgets', 'features', 'entities', 'shared', 'processes'],
  widgets: ['features', 'entities', 'shared', 'processes'],
  features: ['entities', 'shared', 'processes'],
  entities: ['shared', 'processes'],
  shared: ['processes'],
  processes: [],
}

// Найти все TypeScript/JavaScript файлы
function findFiles(pattern) {
  return glob.sync(pattern, {
    ignore: ['node_modules/**', '.next/**', 'dist/**'],
  })
}

// Определить слой файла
function getFileLayer(filePath) {
  const relativePath = path.relative(process.cwd(), filePath)
  const segments = relativePath.split(path.sep)

  for (const layer of FSD_LAYERS) {
    if (segments.includes(layer)) {
      return layer
    }
  }

  return null
}

// Извлечь импорты из файла
function extractImports(filePath) {
  const content = fs.readFileSync(filePath, 'utf8')
  const importRegex = /import\s+.*?from\s+['"]([^'"]+)['"]/g
  const imports = []

  let match
  while ((match = importRegex.exec(content)) !== null) {
    const importPath = match[1]

    // Пропускаем внешние импорты
    if (
      !importPath.startsWith('@/') &&
      !importPath.startsWith('./') &&
      !importPath.startsWith('../')
    ) {
      continue
    }

    // Определяем слой импорта
    let importLayer = null
    if (importPath.startsWith('@/')) {
      const segments = importPath.split('/')
      for (const layer of FSD_LAYERS) {
        if (segments.includes(layer)) {
          importLayer = layer
          break
        }
      }
    }

    imports.push({
      path: importPath,
      layer: importLayer,
    })
  }

  return imports
}

// Проверить правила импортов
function checkImportRules(filePath, imports) {
  const fileLayer = getFileLayer(filePath)
  if (!fileLayer) return []

  const allowedLayers = IMPORT_RULES[fileLayer] || []
  const violations = []

  for (const importItem of imports) {
    if (importItem.layer && !allowedLayers.includes(importItem.layer)) {
      violations.push({
        file: filePath,
        import: importItem.path,
        fromLayer: fileLayer,
        toLayer: importItem.layer,
        message: `Слой '${fileLayer}' не может импортировать слой '${importItem.layer}'`,
      })
    }
  }

  return violations
}

// Проверить структуру папок
function checkFolderStructure() {
  const violations = []

  for (const layer of FSD_LAYERS) {
    const layerPath = path.join(process.cwd(), layer)
    if (fs.existsSync(layerPath)) {
      const stats = fs.statSync(layerPath)
      if (!stats.isDirectory()) {
        violations.push({
          type: 'structure',
          message: `'${layer}' должен быть папкой, а не файлом`,
        })
      }
    }
  }

  return violations
}

// Проверить наличие index.ts файлов
function checkIndexFiles() {
  const violations = []

  for (const layer of FSD_LAYERS) {
    const layerPath = path.join(process.cwd(), layer)
    const indexPath = path.join(layerPath, 'index.ts')

    if (fs.existsSync(layerPath) && !fs.existsSync(indexPath)) {
      violations.push({
        type: 'index',
        layer,
        message: `Отсутствует index.ts в слое '${layer}'`,
      })
    }
  }

  return violations
}

// Основная функция проверки
function checkFSD() {
  console.log('🔍 Проверка FSD архитектуры...\n')

  const violations = []

  // Проверка структуры папок
  const structureViolations = checkFolderStructure()
  violations.push(...structureViolations)

  // Проверка index файлов
  const indexViolations = checkIndexFiles()
  violations.push(...indexViolations)

  // Проверка импортов
  const tsFiles = findFiles('**/*.{ts,tsx}')
  let importViolations = []

  for (const file of tsFiles) {
    const imports = extractImports(file)
    const fileViolations = checkImportRules(file, imports)
    importViolations.push(...fileViolations)
  }

  violations.push(...importViolations)

  // Вывод результатов
  if (violations.length === 0) {
    console.log('✅ FSD архитектура корректна!')
    return true
  } else {
    console.log('❌ Найдены нарушения FSD архитектуры:\n')

    const structureErrors = violations.filter((v) => v.type === 'structure')
    const indexErrors = violations.filter((v) => v.type === 'index')
    const importErrors = violations.filter((v) => !v.type)

    if (structureErrors.length > 0) {
      console.log('📁 Ошибки структуры:')
      structureErrors.forEach((v) => console.log(`  - ${v.message}`))
      console.log()
    }

    if (indexErrors.length > 0) {
      console.log('📄 Отсутствующие index.ts файлы:')
      indexErrors.forEach((v) => console.log(`  - ${v.message}`))
      console.log()
    }

    if (importErrors.length > 0) {
      console.log('🔄 Нарушения правил импортов:')
      importErrors.forEach((v) => {
        console.log(`  - ${v.file}`)
        console.log(`    ${v.message}`)
        console.log(`    Импорт: ${v.import}`)
        console.log()
      })
    }

    return false
  }
}

// Запуск проверки
if (require.main === module) {
  const success = checkFSD()
  process.exit(success ? 0 : 1)
}

module.exports = { checkFSD }
