export default function colorForUncertainty (category, certainty, taxonomy) {
  const certaintyLevelTransparencies = {
    'very high': 'f0',
    high: 'e0',
    medium: 'c0',
    low: 'a6',
    'very low': '90',
    unknown: '30'
  }

  if (certainty === 'unknown') {
    return 'lightgrey'
  } else if (taxonomy &&
      Object.hasOwnProperty.call(taxonomy, category) &&
      Object.hasOwnProperty.call(certaintyLevelTransparencies, certainty)) {
    return taxonomy[category].color + certaintyLevelTransparencies[certainty]
  } else {
    return '#fff'
  }
}
