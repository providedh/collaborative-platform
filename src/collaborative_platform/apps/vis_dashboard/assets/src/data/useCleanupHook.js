import React, {useEffect} from 'react';

export default function useCleanup(dataClient){
    useEffect(()=>dataClient.clearFiltersAndSubscriptions, []);
};