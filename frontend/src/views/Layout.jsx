import { Link, Outlet, useNavigate } from 'react-router';
import { Card } from 'primereact/card';
import { TabMenu } from 'primereact/tabmenu';

export default function Layout(){

    const navigate = useNavigate();
    
    const menuItems = [
        { label: 'Home', icon: 'pi pi-home', command: () => navigate("/") },
        { label: 'Profile', icon: 'pi pi-user', command: () => navigate("/profile") },
        { label: 'Settings', icon: 'pi pi-cog', command: () => navigate("/settings") }
    ];

    return (
        <>
            <Card title="EventRoster">
                <TabMenu model={menuItems} />
            </Card>

            <Outlet />
        </>
    )
}