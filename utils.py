def reformat_X(X, long_name, method):
    """
    Reformat data input for regression (columns become model id and rows become dates)
    
    Inputs
    ------
        X (pd.Dataframe): original dataframe of original and bias corrected climate model timeframes to use for prediction
        method (String): either bias corrected or raw model time series data
        
    Inputs
    ------
        X_formatted (pd.Dataframe): reformatted and pivoted dataframe for direct input into regression
        
    """
    X_formatted = X.loc[X['Method']==method]
    del X_formatted["Method"]
    X_formatted = X_formatted.pivot(columns="Climate Model ID", values=long_name)
    #X_formatted.fillna(0, inplace=True)
    #X_formatted.replace(np.inf, 0)
    #print(X_formatted.stack().mean())
    return X_formatted