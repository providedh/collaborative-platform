/* Class: Director
 *
 * 
 * */
export default function Director(builder){
	const self = {};

	function _init(builder){
		self._builder = builder;

		self.make = _make;
		self.changeBuilder = _changeBuilder;
		
		return self;
	}

	function _changeBuilder(builder){
		self._builder = builder;
	}

	function _make(colorScaleName, rangeScaleName, eventCallback){
		self._builder.resetBuild();
		self._builder.setColorScale(colorScaleName);
		self._builder.setRangeScale(rangeScaleName);
		self._builder.setEventCallback(eventCallback);
		self._builder.setLayout();
	}

	return _init(builder);
}