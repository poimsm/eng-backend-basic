export const fetchCategories = async () => {
    const response = await fetch('/movies');
    const categories = await response.json();
    return categories;
}