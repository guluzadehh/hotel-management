$(document).ready(function () {
    function displayReservations(data) {
        const reservation_list = $('#reservation-list');

        reservation_list.empty();

        if (data.length == 0) {
            reservation_list.append(`
                <div class="d-flex justify-content-center align-items-center">
                    <h3 class="text-muted">Пусто</h3>
                </div>`
            );
            return;
        }

        for (const reservation of data) {
            reservation_list.append(
                `<div class="reservation-item p-2 mt-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <h4>Комната ${reservation['room']['number']}</h4>
                        <p>${reservation['guest']['get_full_name']}</p>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <p>От: ${reservation['start_date']}</p>
                            <p>До: ${reservation['end_date']}</p>
                        </div>
                        <div>
                            <p>Цена: ${reservation['room']['price_per_day']}</p>
                            <p>Общая цена: ${reservation['total_price']}</p>
                        </div>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <p>Кол-во мест: ${reservation['room']['beds']}</p>
                        </div>
                        <div>
                            <button type="button" class="btn btn-danger btn-cancel" data-reservation-id="${reservation['id']}">Отменить</button>
                        </div>
                    </div>
                </div>`
            );
        }
    }

    const fetchReservations = (url) => {
        $.ajax({
            method: 'GET',
            url: url,
            success: json => displayReservations(json),
        })
    }

    fetchReservations('/api/reservations/');

    let url = new URL('http://127.0.0.1:8000/api/reservations/');

    $('#reservation-list').on('click', '.btn-cancel', function () {
        const reservation_id = $(this).attr('data-reservation-id');
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            method: 'DELETE',
            headers: {
                'X-CSRFTOKEN': csrftoken,
            },
            url: `/api/reservations/${reservation_id}`,
            success: () => {
                fetchReservations(url);
                new bootstrap.Toast($('.toast')).show();
            },
        })
    });

    $('.filter').on('click', '#filter-btn', function () {
        const all = $('input[name="all"]:checked').val();
        if (all == 'true') {
            url.searchParams.set('all', true)
        }
        fetchReservations(url);
    });
});