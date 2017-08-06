{/*
  TODOS:
    - Make fields for Row component configurable by props passed to
      PaginatedTable component
    - Build out missing column data (req's API changes)
    - Add search functionality (req's API changes)
    - Add order_by functionaltiy (req's API changes)
    - Encode offset, count, limit, search, order_by in URL
    - Support internationalization of component text
*/}

class PaginatedTable extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      data: [],
      loading: null,
      err: null,

      limit: props.limit,
      offset: 0,
      count: 0,
    }
  }

  componentDidMount() {
    this.fetchData()
  }

  fetchData(loading = true){
    this.setState({loading, err: null})
    let url = `${this.props.url}?limit=${this.state.limit}&offset=${this.state.offset}`
    fetch(url, {
      credentials: "same-origin",
    })
    .catch(err => {
      this.setState({
        loading: false,
        err: true
      })
    })
    .then(result => result.json())
    .then(data => {
      this.setState({
        data: data['results'],
        loading: false,
        count: data['count'],
      })
    })
  }

  changePage(event, direction){
    event.preventDefault()
    this.setState(
      previousState => {
        let change = (direction * previousState.limit);
        return {
          offset: Math.max(previousState.offset + change, 0)
        }
      },
      () => this.fetchData()
    )

  }

  changeLimit(event) {
    this.setState(
      {limit: Number(event.target.value)},
      () => this.fetchData(false)
    )
  }

  render() {
    return (
      <div className="dataTables_wrapper form-inline dt-bootstrap no-footer">
        <SearchField />
        <table id="paginated-table" className="table table-hover dataTable">
          <thead>
            <tr>
              {this.props.layout.map(column => {
                let {title, columns} = column
                return <th className={ `col-md-${columns} hidden-xs hidden-sm` }>{ title }</th>
              })}
            </tr>
          </thead>
          <tbody>
            {
              this.state.loading || this.state.err ?
                <td colSpan="100%" style={{"text-align": "center", padding: "10px"}}>
                  { this.state.loading ? "Loading..." : "Error fetching data"} {/* TODO: Support internationalization */}
                </td> : this.state.data.map(obj => <Row data={ obj } /> )
            }
          </tbody>
        </table>
        <PaginationNav
          onChange={this.changePage.bind(this)}
          showNext={(this.state.limit + this.state.offset) < this.state.count }
          showPrev={this.state.offset > 0 }
        />
        <PaginationInfo
          offset={this.state.offset}
          count={this.state.count}
          length={this.state.data.length}
        />
        <PerPageDropdown
          value={this.state.limit}
          onChange={this.changeLimit.bind(this)}
        />
      </div>
    )
  }
}


function Row(props) {
  {/* TODO:
      This will vary based on data being represented. Should be
      configurable via props somehow
  */}
  return (
    <tr>
      <td>
        <div className="media-left">
          <img src={ props.data.thumbnail || '' } className="thumb-60" />
        </div>
        <div className="media-body">
          <p>
            <a href={ `${ props.data.id }/` }>
              <strong>{ props.data.name }</strong>
            </a>
            <br />
            { props.data.original_file }
          </p>
        </div>
      </td>
      <td className="hidden-xs hidden-sm">
        { props.data.file } <em>todo: this seems wrong</em>
      </td>
      <td className="hidden-xs hidden-sm">
        <em>todo: contributor</em>
      </td>
      <td className="hidden-xs hidden-sm">
        <em>todo: last_updated</em>
      </td>
      <td className="hidden-xs hidden-sm">
        <em>todo: attached_to</em>
      </td>
    </tr>
  )
}


function SearchField(props) {
  return (
    <div className="table-search clearfix">
      <div className="dataTables_filter">
        <label>
          <div className="input-group">
            <span className="input-group-addon">
              <span className="glyphicon glyphicon-search"></span>
            </span>
            <input
              type="search"
              className="form-control input-sm"
              placeholder="Search"
              aria-controls="paginated-table"
            />
          </div>
        </label>
      </div>
    </div>
  )
}


function PaginationNav(props) {
  return (
    <div className="table-pagination">
      <div className="dataTables_paginate paging_simple">
        <ul className="pagination">
          <li
            className={ `paginate_button previous ${ !props.showPrev && "disabled" }` }
            onClick={(e) => props.showPrev && props.onChange(e, -1)}
          >
            <a href="#" aria-controls="paginated-table" tabindex="0">
              <span className="glyphicon glyphicon-triangle-left"></span>
            </a>
          </li>
          <li
            className={ `paginate_button next ${ !props.showNext && "disabled" }` }
            onClick={(e) => props.showNext && props.onChange(e, 1)}
          >
            <a href="#" aria-controls="paginated-table" tabindex="0">
              <span className="glyphicon glyphicon-triangle-right"></span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  )
}


function PaginationInfo(props) {
  return (
    <div className="table-entries">
      <div className="dataTables_info" role="status" aria-live="polite">
        Showing {props.length ? props.offset + 1 : 0} - {props.offset + props.length} of {props.count}
      </div>
    </div>
  )
}


function PerPageDropdown(props) {
  return (
    <div className="table-num">
      <div className="dataTables_length">
        <label>
          <select
            className="form-control input-sm"
            value={props.value}
            onChange={props.onChange}
          >
            <option value="10" >10 per page</option>
            <option value="25">25 per page</option>
            <option value="50">50 per page</option>
            <option value="100">100 per page</option>
          </select>
        </label>
      </div>
    </div>
  )
}
