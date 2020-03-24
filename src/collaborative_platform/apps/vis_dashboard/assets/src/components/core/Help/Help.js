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
                        <h5><i>Display distributions by encoding the information with bars.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                Bar charts allow to easily display distributions such as the
                                named entities per document, common values for certain entity
                                attribute, or the level of certainty associated to a category.
                            </p>
                            <p>
                                Hovering over the bars will display a tooltip with the bar information.
                            </p>
                            <p>
                                Filtering can be done by clicking on the bars. Once a bar has been selected,
                                add more to the selection by clicking on more.<br/>
                                Undo the filtering by clicking again on a selected bar.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>Bar direction</b><br/> 
                                    Toggle between a horizontal or a vertical layout based
                                    on your necessities.
                                </li>
                                <li><b>Dimension</b><br/>
                                    Set the information displayed in the bar chart. The data used
                                    take into account the selected project version and filtering 
                                    done through other views.
                                </li>
                                <li><b>Render overlay</b><br/>
                                    Toggle an overlay showing additional information in the graph.</li>
                                <li><b>Overlay</b><br/>
                                    Select the information rendered in the bars overlay. It will
                                    only be shown if the overlay is set to be rendered.</li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Number of entities per document</li>
                                <li className="list-group-item">Number of entities per type</li>
                                <li className="list-group-item">Most common entities</li>
                                <li className="list-group-item">Annotation count by document</li>
                                <li className="list-group-item">Annotation count by category</li>
                                <li className="list-group-item">Annotation count by entity</li>
                                <li className="list-group-item">Most common attributes</li>
                                <li className="list-group-item">Attribute values</li>
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
                                <li><b>Sort documents by</b><br/> 
                                    Sort documents to better see what the state is for more recent,
                                    larger, or most contributed documents is.
                                </li>
                                <li><b>Color certainty by</b><br/>
                                    Choose what will be shown in the complimentary view. This second 
                                    representation of the corpus allows to see how the category, source,
                                    entity type, or other aspects are annotated along the document collection.
                                </li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Eligible options for certainty representation</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Category</li>
                                <li className="list-group-item">Certainty level</li>
                                <li className="list-group-item">Category and certainty level</li>
                                <li className="list-group-item">Authorship</li>
                                <li className="list-group-item">Entity type</li>
                                <li className="list-group-item">Locus</li>
                                <li className="list-group-item">Last edit time</li>
                                <li className="list-group-item">Amount of annotations</li>
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
                                <li><b>Tile layout</b><br/> 
                                    Toggle between a regular, split, or tile layout for the grid; which 
                                    allows to remove redundant information for the eligible options.
                                </li>
                                <li><b>Color scale</b><br/> 
                                    Choose between a set of available color schemes for encoding the 
                                    selected dimension.
                                </li>
                                <li><b>Range scale</b><br/> 
                                    Choose what type of transformation will be applied to the data, allowing
                                    the least or most represented entries to be more visible.
                                </li>
                                <li><b>Dimension</b><br/> 
                                    Choose what information will be displayed in the visualization.
                                </li>
                            </ul>
                        </div>
                        <div className="col-sm">
                            <p>Available dimensions</p>
                            <ul className="list-group ">
                                <li className="list-group-item">Documents related by entities</li>
                                <li className="list-group-item">Entities related by documents</li>
                              </ul>
                        </div>
                    </div>
                    <hr/>
                </div>
                <div>
                    <div className="row ml-0 mr-0">
                        <h2>Document view</h2>
                    </div>
                    <div className="row ml-0 mr-0">
                        <h5><i>Display the contents of a project's document.</i></h5>
                    </div>
                    <div className="row mt-2">
                        <div className="col-sm">
                            <p>
                                This widget renders the contents of a document using the current taxonomy configuration,
                                and navigating to the <i>Annotator</i> with the selected document.
                            </p>
                        </div>
                        <div className="col-sm">
                            <h5>Configuration Parameters</h5>
                            <ul>
                                <li><b>Sync with views</b><br/> 
                                    If selected, the document shown in this view will be the focused document; changed
                                    by interacting (clicking) with the rest of views.
                                </li>
                                <li><b>Document</b><br/> 
                                    <em>Available when the view is not synched</em>, allows to choose what document is shown.
                                    When the document is selected manually, interacting with other views will not affect it.
                                </li>
                            </ul>
                        </div>
                        <div className="col-sm">
                        </div>
                    </div>
                    <hr/>
                </div>
                <div className="d-none">
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
                <div className="d-none">
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
                <div className="d-none">
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
                <div className="d-none">
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
