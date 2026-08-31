import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('Alfchamps UI error:', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="error-box" style={{ marginTop: 24 }}>
          <h3 style={{ marginTop: 0 }}>Something went wrong rendering this page.</h3>
          <p>{String(this.state.error && this.state.error.message ? this.state.error.message : this.state.error)}</p>
          <button className="btn" onClick={() => window.location.reload()}>
            Reload
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
