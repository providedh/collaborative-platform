import React from 'react';

export default class Text extends React.PureComponent {
    constructor(props) {
        super(props);
    }

    render() {
        return <p>{this.props.text}</p>
    }
}
