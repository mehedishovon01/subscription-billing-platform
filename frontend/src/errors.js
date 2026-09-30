export function formatApiError(err, fallback = 'Request failed.') {
  const data = err && err.response && err.response.data
  if (!data) {
    return fallback
  }
  if (typeof data === 'string') {
    return data
  }
  if (data.detail) {
    return Array.isArray(data.detail) ? data.detail.join(' ') : String(data.detail)
  }
  if (data.non_field_errors) {
    return Array.isArray(data.non_field_errors)
      ? data.non_field_errors.join(' ')
      : String(data.non_field_errors)
  }
  const messages = Object.keys(data).map((key) => {
    const value = data[key]
    if (Array.isArray(value)) {
      return `${key}: ${value.join(' ')}`
    }
    if (value && typeof value === 'object') {
      return `${key}: ${JSON.stringify(value)}`
    }
    return `${key}: ${value}`
  })
  return messages.length ? messages.join(' | ') : fallback
}
