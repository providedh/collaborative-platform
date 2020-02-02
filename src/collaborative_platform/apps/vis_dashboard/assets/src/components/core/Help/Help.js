import React from 'react';
import styles from './style.module.css';
import css from './style.css';

export default function Help(props){
    return(
        <div id="help" className={'container shadow-lg pt-2 hidden '+styles.help}>
            <h3>
                Views in the PROVIDEDH Visualization Dashboard
                <button type="button" onClick={()=>document.getElementById('help').classList.add('hidden')} className="close mt-2 mr-2" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
            </h3>
            <hr/>
            <div className={styles.overflowContainer}>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Bar chart</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Chord Diagram</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Pixel Document</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Pixel Corpus</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Heatmap</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Map</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Violin Plot</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Timeline</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display distributions encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>barDirection</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>renderOverlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Number of annotations per document</li>
                                <li className="list-group-item">Number of annotations per category</li>
                                <li className="list-group-item">Frequency for an attribute's values</li>
                                <li className="list-group-item">Frequency for most common attribute values</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
            </div>
        </div>
        );
}
