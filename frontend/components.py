"""
Reusable UI components for the Streamlit frontend
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any
import datetime


def add_log(message: str):
    """Add a timestamped log entry"""
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")


def display_logs():
    """Display activity logs with export functionality"""
    from api_client import api_client
    from datetime import datetime

    with st.sidebar:
        st.subheader("📋 Activity Logs")

        # Display session logs
        if st.session_state.get('logs', []):
            # Show log count
            total_logs = len(st.session_state.logs)
            st.caption(f"📊 Showing last 15 of {total_logs} session logs")

            # Show last 15 logs in reverse order (newest first)
            for log in reversed(st.session_state.logs[-15:]):
                # Color code different log types
                if "ERROR" in log or "❌" in log:
                    st.error(log, icon="❌")
                elif "SUCCESS" in log or "✅" in log:
                    st.success(log, icon="✅")
                elif "WARNING" in log or "⚠️" in log:
                    st.warning(log, icon="⚠️")
                else:
                    st.info(log, icon="ℹ️")
        else:
            st.info("No activity yet...", icon="📝")

        # View all session logs
        if st.session_state.get('logs', []) and len(st.session_state.logs) > 15:
            with st.expander(f"📜 View All {len(st.session_state.logs)} Session Logs"):
                for log in reversed(st.session_state.logs):
                    st.text(log)

        # Log Export Section
        st.markdown("---")
        st.subheader("📥 Comprehensive Log Export")
        st.caption("Export detailed backend logs including LOCKUP process details")

        # Get log summary from backend
        log_summary = api_client.get_log_summary()

        if log_summary.get("session_logs_count", 0) > 0:
            # Show log statistics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Backend Logs", log_summary.get("session_logs_count", 0),
                         help="Application-level logs from backend")
            with col2:
                st.metric("Operation Logs", log_summary.get("detailed_logs_count", 0),
                         help="Detailed operation logs (LOCKUP, processing, etc.)")

            # Export format selection
            export_format = st.selectbox(
                "Export format:",
                ["text", "csv", "json"],
                help="Choose format for comprehensive log export",
                key="log_export_format"
            )

            # Export button
            if st.button("📥 Export All Logs", type="primary", key="export_logs_btn"):
                with st.spinner("Exporting comprehensive logs..."):
                    log_content = api_client.export_logs(export_format)
                    if log_content:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"etl_comprehensive_logs_{timestamp}.{export_format}"

                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=log_content,
                            file_name=filename,
                            mime=f"text/{export_format}" if export_format != "json" else "application/json",
                            key="download_logs_btn"
                        )
                        add_log(f"Comprehensive logs exported as {export_format}")

            # Clear backend logs button
            if st.button("🗑️ Clear Backend Logs", type="secondary", key="clear_backend_logs"):
                clear_result = api_client.clear_logs()
                if clear_result.get("success"):
                    add_log("Backend logs cleared")
                    st.success("Backend logs cleared successfully")
                    st.rerun()
        else:
            st.info("No backend logs available for export")

        st.markdown("---")

        # Clear session logs button
        if st.button("🗑️ Clear Session Logs", key="clear_session_logs"):
            st.session_state.logs = []
            add_log("Session logs cleared")
            st.rerun()


def display_kpi_metrics(kpi_counts: Dict[str, int], total_records: int):
    """Display KPI metrics in columns"""
    st.subheader("📊 Activation Status KPIs")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Records", total_records)
    with col2:
        st.metric("Status '0'", kpi_counts.get('0', 0))
    with col3:
        st.metric("Status 'D'", kpi_counts.get('D', 0))
    with col4:
        st.metric("Status 'X'", kpi_counts.get('X', 0))
    with col5:
        st.metric("Not Found", kpi_counts.get('NOT_FOUND', 0))


def create_status_chart(kpi_counts: Dict[str, int]):
    """Create a bar chart for activation status distribution"""
    if not kpi_counts:
        return None

    # Prepare data for chart
    labels = list(kpi_counts.keys())
    values = list(kpi_counts.values())
    total = sum(values) if values else 1
    percentages = [v/total*100 for v in values]

    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            name='Count',
            marker_color=px.colors.qualitative.Set3[:len(labels)],
            text=[f'{v}<br>({p:.1f}%)' for v, p in zip(values, percentages)],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<br>Percentage: %{customdata:.1f}%<extra></extra>',
            customdata=percentages
        )
    ])

    # Update layout
    fig.update_layout(
        title="Activation Status Distribution",
        height=400,
        font=dict(size=12),
        showlegend=False,
        xaxis_title="Activation Status",
        yaxis_title="Count"
    )

    return fig


def fix_dataframe_types(df: pd.DataFrame) -> pd.DataFrame:
    """Fix DataFrame data types to prevent PyArrow serialization errors"""
    df = df.copy()

    for col in df.columns:
        # Convert all object columns to string to avoid mixed type issues
        if df[col].dtype == 'object':
            # Handle mixed types by converting everything to string
            df[col] = df[col].astype(str)
            # Replace 'nan' strings with empty strings for cleaner display
            df[col] = df[col].replace(['nan', 'None', 'NaN'], '')

        # Handle numeric columns that might have mixed types
        elif df[col].dtype in ['int64', 'float64']:
            # Ensure numeric columns are properly typed
            try:
                # Try to convert to numeric, coercing errors to NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill NaN with 0 for display purposes
                df[col] = df[col].fillna(0)
            except:
                # If conversion fails, convert to string
                df[col] = df[col].astype(str)

    return df


def display_dataframe_with_search(df: pd.DataFrame, key: str):
    """Display dataframe with search functionality"""
    if df.empty:
        st.warning("No data to display")
        return

    # Fix data types for Arrow compatibility
    df = fix_dataframe_types(df)

    # Search functionality
    search_term = st.text_input(
        "🔍 Search in data:",
        key=f"search_{key}",
        help="Search across all columns"
    )

    # Filter dataframe based on search
    if search_term:
        # Create a mask for rows containing the search term in any column
        mask = df.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning(f"No results found for '{search_term}'")
            return
        else:
            st.info(f"Found {len(filtered_df)} results for '{search_term}'")
    else:
        filtered_df = df

    # Display total count
    st.write(f"**Total records:** {len(filtered_df)}")

    # Display the dataframe
    st.dataframe(filtered_df, use_container_width=True, height=400)


def create_distribution_chart(distribution: Dict[str, int], title: str = "Status Distribution"):
    """Create a bar chart with line overlay for status distribution"""
    if not distribution or sum(distribution.values()) == 0:
        return None

    # Filter out zero values for cleaner chart
    filtered_dist = {k: v for k, v in distribution.items() if v > 0}

    if not filtered_dist:
        return None

    # Prepare data
    categories = list(filtered_dist.keys())
    values = list(filtered_dist.values())
    total = sum(values)
    percentages = [v/total*100 for v in values]

    # Color mapping
    color_map = {
        'X': '#ff6b6b',      # Red for X (active)
        'D': '#4ecdc4',      # Teal for D (discontinued)
        '0': '#45b7d1',      # Blue for 0 (inactive)
        'OTHER': '#96ceb4'   # Green for other
    }
    colors = [color_map.get(cat, '#95a5a6') for cat in categories]

    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            name='Count',
            marker_color=colors,
            text=[f'{v}<br>({p:.1f}%)' for v, p in zip(values, percentages)],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<br>Percentage: %{text}<extra></extra>'
        ),
        secondary_y=False,
    )

    # Add line with dots for percentage
    fig.add_trace(
        go.Scatter(
            x=categories,
            y=percentages,
            mode='lines+markers',
            name='Percentage',
            line=dict(color='#2c3e50', width=3),
            marker=dict(size=10, color='#e74c3c', line=dict(width=2, color='white')),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>Percentage: %{y:.1f}%<extra></extra>'
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title=title,
        height=450,
        font=dict(size=12),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Count", secondary_y=False)
    fig.update_yaxes(title_text="Percentage (%)", secondary_y=True)
    fig.update_xaxes(title_text="Status Categories")

    return fig


def create_comparison_chart(original_dist: Dict[str, int], new_dist: Dict[str, int]):
    """Create a comparison chart with bars and line overlay showing before vs after"""
    if not original_dist or not new_dist:
        return None

    # Prepare data for comparison
    categories = list(set(original_dist.keys()) | set(new_dist.keys()))
    original_values = [original_dist.get(cat, 0) for cat in categories]
    new_values = [new_dist.get(cat, 0) for cat in categories]

    # Calculate changes
    changes = [new - orig for orig, new in zip(original_values, new_values)]

    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add grouped bar chart
    fig.add_trace(
        go.Bar(
            name='Before Processing',
            x=categories,
            y=original_values,
            marker_color='#3498db',
            text=original_values,
            textposition='auto',
            offsetgroup=1,
            hovertemplate='<b>%{x}</b><br>Before: %{y}<extra></extra>'
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            name='After Processing',
            x=categories,
            y=new_values,
            marker_color='#2c3e50',
            text=new_values,
            textposition='auto',
            offsetgroup=2,
            hovertemplate='<b>%{x}</b><br>After: %{y}<extra></extra>'
        ),
        secondary_y=False,
    )

    # Add line plot showing changes with dots
    fig.add_trace(
        go.Scatter(
            x=categories,
            y=changes,
            mode='lines+markers',
            name='Net Change',
            line=dict(color='#e74c3c', width=3),
            marker=dict(
                size=12,
                color=['#27ae60' if c >= 0 else '#e74c3c' for c in changes],
                line=dict(width=2, color='white')
            ),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>Change: %{y:+d}<extra></extra>'
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title='Distribution Comparison: Before vs After Processing',
        height=450,
        font=dict(size=12),
        showlegend=True,
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Number of Items", secondary_y=False)
    fig.update_yaxes(title_text="Net Change", secondary_y=True)
    fig.update_xaxes(title_text="Status Categories")

    return fig


def create_processing_flow_chart(processing_stats: Dict[str, Any]):
    """Create a horizontal bar chart showing processing flow statistics"""
    if not processing_stats:
        return None

    # Prepare data for processing flow
    total_checked = processing_stats.get("total_checked", 0)
    not_in_target = processing_stats.get("not_in_target_count", 0)
    updated_count = processing_stats.get("updated_count", 0)
    in_target = total_checked - not_in_target
    other_status = not_in_target - updated_count

    # Create data for horizontal bar chart
    categories = [
        'Total Items Checked',
        'Items in Target Sheet',
        'Items NOT in Target',
        'Status X (Updated to D)',
        'Other Status (Unchanged)'
    ]

    values = [
        total_checked,
        in_target,
        not_in_target,
        updated_count,
        other_status
    ]

    # Color scheme for different categories
    colors = [
        '#3498db',  # Blue for total
        '#2ecc71',  # Green for in target
        '#f39c12',  # Orange for not in target
        '#e74c3c',  # Red for updated
        '#95a5a6'   # Gray for other
    ]

    # Create horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(
            y=categories,
            x=values,
            orientation='h',
            marker_color=colors,
            text=values,
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
        )
    ])

    # Add line plot overlay showing processing efficiency
    if total_checked > 0:
        efficiency_categories = ['Processing Efficiency', 'Update Rate', 'Target Coverage']
        efficiency_values = [
            (updated_count / not_in_target * 100) if not_in_target > 0 else 0,  # Update efficiency
            (updated_count / total_checked * 100),  # Overall update rate
            (in_target / total_checked * 100)  # Target coverage
        ]

        # Create secondary subplot for efficiency metrics
        fig.add_trace(
            go.Scatter(
                x=efficiency_values,
                y=efficiency_categories,
                mode='lines+markers',
                name='Efficiency %',
                line=dict(color='#9b59b6', width=3),
                marker=dict(size=12, color='#8e44ad', line=dict(width=2, color='white')),
                yaxis='y2',
                xaxis='x2',
                hovertemplate='<b>%{y}</b><br>Percentage: %{x:.1f}%<extra></extra>'
            )
        )

    fig.update_layout(
        title="Pre-existing Items Processing Flow Analysis",
        height=450,
        font=dict(size=12),
        showlegend=True,
        xaxis_title="Number of Items",
        yaxis_title="Processing Categories",
        margin=dict(l=200, r=50, t=50, b=50)
    )

    return fig


def create_trend_analysis_chart(data_series: List[Dict[str, Any]], title: str = "Trend Analysis"):
    """Create a line chart with dots for trend analysis"""
    if not data_series:
        return None

    # Extract data for plotting
    x_values = [item.get('label', f'Point {i+1}') for i, item in enumerate(data_series)]
    y_values = [item.get('value', 0) for item in data_series]

    # Create line chart with markers
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines+markers',
            name='Trend',
            line=dict(color='#3498db', width=3),
            marker=dict(
                size=12,
                color='#e74c3c',
                line=dict(width=2, color='white')
            ),
            hovertemplate='<b>%{x}</b><br>Value: %{y}<extra></extra>'
        )
    )

    # Add area fill under the line
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            fill='tonexty',
            mode='none',
            fillcolor='rgba(52, 152, 219, 0.2)',
            name='Area',
            showlegend=False
        )
    )

    fig.update_layout(
        title=title,
        height=400,
        font=dict(size=12),
        showlegend=True,
        xaxis_title="Categories",
        yaxis_title="Values"
    )

    return fig


def create_progress_bar(current_step: int, total_steps: int, step_names: List[str]):
    """Create a progress bar showing current step"""
    progress = current_step / total_steps

    st.progress(progress)

    # Show step indicators
    cols = st.columns(total_steps)
    for i, (col, step_name) in enumerate(zip(cols, step_names)):
        with col:
            if i < current_step:
                st.success(f"✅ {step_name}")
            elif i == current_step:
                st.info(f"🔄 {step_name}")
            else:
                st.write(f"⏳ {step_name}")


def display_file_info(filename: str, sheet_names: List[str]):
    """Display file information in an info box"""
    st.info(f"""
    **File:** {filename}  
    **Sheets:** {len(sheet_names)}  
    **Sheet Names:** {', '.join(sheet_names)}
    """)


def create_download_section(download_url: str, filename: str, data_preview: List[Dict]):
    """Create download section with preview"""
    st.subheader("📥 Download Results")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**File:** {filename}")
        st.write(f"**Records:** {len(data_preview)}")
    
    with col2:
        st.download_button(
            label="📥 Download CSV",
            data="",  # This would be populated with actual data
            file_name=filename,
            mime="text/csv",
            help="Download the complete processed dataset"
        )


def display_error_message(error: str, details: str = None):
    """Display error message with optional details"""
    st.error(f"❌ {error}")
    if details:
        with st.expander("Error Details"):
            st.code(details)


def display_success_message(message: str):
    """Display success message"""
    st.success(f"✅ {message}")


def create_sidebar_navigation():
    """Create sidebar navigation menu"""
    with st.sidebar:
        st.title("🔧 ETL Automation Tool")
        
        # Navigation menu
        selected = st.selectbox(
            "Navigation",
            ["📁 File Upload", "🧹 Data Cleaning", "🔍 Data Lookup", "📊 Results"],
            key="navigation"
        )
        
        return selected.split(" ", 1)[1]  # Return just the text part
