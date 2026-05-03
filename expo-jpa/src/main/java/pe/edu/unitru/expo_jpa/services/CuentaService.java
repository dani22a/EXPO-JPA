package pe.edu.unitru.expo_jpa.services;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.unitru.expo_jpa.dto.CrearCuentaRequest;
import pe.edu.unitru.expo_jpa.dto.CrearMovimientoRequest;
import pe.edu.unitru.expo_jpa.dto.CuentaDto;
import pe.edu.unitru.expo_jpa.dto.MovimientoDto;
import pe.edu.unitru.expo_jpa.entities.Cliente;
import pe.edu.unitru.expo_jpa.entities.Cuenta;
import pe.edu.unitru.expo_jpa.entities.Movimiento;
import pe.edu.unitru.expo_jpa.entities.TipoMovimiento;
import pe.edu.unitru.expo_jpa.exceptions.RecursoNoEncontradoException;
import pe.edu.unitru.expo_jpa.exceptions.SaldoInsuficienteException;
import pe.edu.unitru.expo_jpa.repositories.ClienteRepository;
import pe.edu.unitru.expo_jpa.repositories.CuentaRepository;
import pe.edu.unitru.expo_jpa.repositories.MovimientoRepository;

import java.math.BigDecimal;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class CuentaService {

    // Inyección por constructor (campos final + Lombok @RequiredArgsConstructor).
    private final CuentaRepository cuentaRepo;
    private final ClienteRepository clienteRepo;
    private final MovimientoRepository movRepo;

    public CuentaDto obtener(Long id) {
        return aDto(buscar(id));
    }

    // Page<T>.map(...) convierte entidades a DTOs manteniendo la metadata de paginación.
    public Page<CuentaDto> listarPorCliente(Long clienteId, Pageable pageable) {
        return cuentaRepo.findByClienteId(clienteId, pageable).map(this::aDto);
    }

    public BigDecimal saldoTotalDeCliente(Long clienteId) {
        return cuentaRepo.sumarSaldosDeCliente(clienteId);
    }

    // Usa la NATIVE QUERY del repositorio.
    public List<CuentaDto> topCuentasRicas(int limite) {
        return cuentaRepo.topCuentasPorEncimaDelPromedio(limite)
            .stream().map(this::aDto).toList();
    }

    @Transactional
    public CuentaDto crear(CrearCuentaRequest req) {
        // Validación de unicidad ANTES de intentar guardar (mensaje de error más claro).
        if (cuentaRepo.existsByNumeroCuenta(req.numeroCuenta())) {
            throw new IllegalArgumentException("Numero de cuenta ya registrado: " + req.numeroCuenta());
        }
        // El cliente debe existir; si no, 404.
        Cliente cliente = clienteRepo.findById(req.clienteId())
            .orElseThrow(() -> new RecursoNoEncontradoException("Cliente", req.clienteId()));

        Cuenta cuenta = Cuenta.builder()
            .numeroCuenta(req.numeroCuenta())
            .saldo(req.saldoInicial())
            .cliente(cliente)
            .build();

        return aDto(cuentaRepo.save(cuenta));
    }

    /**
     * Registra un movimiento y actualiza el saldo. Es ATÓMICO:
     * si algo falla a mitad, ningún cambio se persiste (rollback automático).
     */
    @Transactional
    public MovimientoDto registrarMovimiento(Long cuentaId, CrearMovimientoRequest req) {
        Cuenta cuenta = buscar(cuentaId);

        // Switch expression (Java 14+): calcula el nuevo saldo según el tipo.
        BigDecimal nuevoSaldo = switch (req.tipo()) {
            case DEPOSITO, TRANSFERENCIA_ENTRANTE ->
                cuenta.getSaldo().add(req.monto());
            case RETIRO, TRANSFERENCIA_SALIENTE, PAGO_SERVICIO -> {
                // Validación de saldo: si no alcanza, 422.
                if (cuenta.getSaldo().compareTo(req.monto()) < 0) {
                    throw new SaldoInsuficienteException(
                        "Saldo %.2f insuficiente para %s de %.2f"
                            .formatted(cuenta.getSaldo(), req.tipo(), req.monto())
                    );
                }
                yield cuenta.getSaldo().subtract(req.monto());
            }
        };

        cuenta.setSaldo(nuevoSaldo);    // dirty checking detecta el cambio

        // Construcción del movimiento + asociación bidireccional con la cuenta.
        Movimiento mov = Movimiento.builder()
            .monto(req.monto())
            .tipo(req.tipo())
            .descripcion(req.descripcion())
            .build();
        cuenta.agregarMovimiento(mov);  // sincroniza ambos lados de la relación

        movRepo.save(mov);              // persiste y obtiene el ID generado
        return aMovimientoDto(mov);
    }

    private Cuenta buscar(Long id) {
        return cuentaRepo.findById(id)
            .orElseThrow(() -> new RecursoNoEncontradoException("Cuenta", id));
    }

    // Mapper: incluye el nombre completo del titular (requiere acceso lazy al cliente).
    // Como estamos dentro de la transacción, el LAZY no rompe.
    private CuentaDto aDto(Cuenta c) {
        return new CuentaDto(
            c.getId(),
            c.getNumeroCuenta(),
            c.getSaldo(),
            c.getFechaApertura(),
            c.getCliente().getId(),
            c.getCliente().getNombres() + " " + c.getCliente().getApellidos()
        );
    }

    private MovimientoDto aMovimientoDto(Movimiento m) {
        return new MovimientoDto(
            m.getId(), m.getMonto(), m.getTipo(),
            m.getDescripcion(), m.getFecha(), m.getCuenta().getId()
        );
    }

    /**
     * Transferencia entre cuentas. La transacción única garantiza atomicidad:
     * si la segunda llamada falla, la primera también se revierte.
     */
    @Transactional
    public void transferir(Long origenId, Long destinoId, BigDecimal monto) {
        if (origenId.equals(destinoId)) {
            throw new IllegalArgumentException("No se puede transferir a la misma cuenta");
        }
        // Resta del origen.
        registrarMovimiento(origenId, new CrearMovimientoRequest(
            monto, TipoMovimiento.TRANSFERENCIA_SALIENTE, "Transferencia a cuenta " + destinoId
        ));
        // Suma al destino. Si esta línea falla, la anterior se revierte (mismo @Transactional).
        registrarMovimiento(destinoId, new CrearMovimientoRequest(
            monto, TipoMovimiento.TRANSFERENCIA_ENTRANTE, "Transferencia desde cuenta " + origenId
        ));
    }
}
