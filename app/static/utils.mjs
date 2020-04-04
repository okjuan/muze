const Utils = {
    ThrowIfNullOrUndefined: (value, msg) => {
        if (msg === undefined) {
            msg = `Value is null or undefined: ${JSON.stringify(value)}`;
        }
        if (value === undefined || value === null) {
            throw new Error(msg);
        }
    },
    ThrowIfNullOrUndefinedOrEmpty: (value, msg) => {
        if (msg === undefined) {
            msg = `Value is null or undefined or empty: ${JSON.stringify(value)}`;
        }
        Utils.ThrowIfNullOrUndefined(value, msg);
        if (value.hasOwnProperty("length") && value.length === 0) {
            throw new Error(msg);
        }
    }
}

export { Utils }