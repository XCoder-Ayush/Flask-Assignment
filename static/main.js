let isFetching = false;
// Function to fetch outline data from the server
async function fetchOutlineByURL(url) {
    try {
        isFetching = true;
        const response = await fetch(url);
        const data = await response.json();
        console.log(data);
        return data;
    } catch (error) {
        console.error('Error fetching outline:', error);
    }finally {
        isFetching = false; // Set flag to false when the request is completed (whether it resolves or rejects)
    }
}
let outlineData
// Function to update the outline HTML
function updateOutlineHTML(outlineData) {
    const outlineContainer = document.getElementById('outline-container');
    outlineContainer.innerHTML = ''; // Clear existing content

    // Function to recursively create outline HTML
    function createOutlineHTML(item) {
        const itemElement = document.createElement('div');
        itemElement.textContent = item.text;
        outlineContainer.appendChild(itemElement);

        // Recursively create child elements
        if (item.children && item.children.length > 0) {
            const childrenContainer = document.createElement('div');
            childrenContainer.classList.add('children-container');
            item.children.forEach(childUrl => {
                const childItem = outlineData[childUrl];
                if (childItem) {
                    const childElement = createOutlineHTML(childItem);
                    childrenContainer.appendChild(childElement);
                }
            });
            outlineContainer.appendChild(childrenContainer);
        }

        return itemElement;
    }

    // Start from the root item
    const rootItem = outlineData
    // console.log(rootItem);
    if (rootItem) {
        createOutlineHTML(rootItem);
    }
}
async function fetchAndUpdateOutline(url) {
    if (isFetching) {
        return; 
    }
    const outlineData = await fetchOutlineByURL(url);
    updateOutlineHTML(outlineData);

    // Recursively fetch and update child outlines
    if (outlineData.children && outlineData.children.length > 0) {
        for (const childURL of outlineData.children) {
            await fetchAndUpdateOutline(childURL);
        }
    }
}
// Function to poll for updates and update the outline
async function pollForUpdates() {
    while (true) {
        await new Promise(resolve => setTimeout(resolve, 5000)); 
        outlineData = await fetchAndUpdateOutline('/outline');
        updateOutlineHTML(outlineData);
    }
}

// Initial setup: Fetch outline and start polling for updates
(async function() {
    await fetchAndUpdateOutline('/outline');
    pollForUpdates();
})();